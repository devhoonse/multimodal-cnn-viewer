# -*- coding: utf-8 -*-
import os
import sys
import ast
import json
import pickle
import logging
import argparse
from configparser import ConfigParser

sys.path.append('/home/istream3/istream/env/backend/lib/python3.6/site-packages/BIMATRIX/')
sys.path.append('/home/istream3/py_codepad/metax_manager/')

from learner_server.utils import DateTimeHandler
from learner_server.configs import ApplicationConfiguration
from learner_server.dao import ProcessDAO, OracleDataSource, AbstractSession

from MCNN.utils import update_config
from MCNN.model.hetero.mcnn import Hetero, Modified_m_CNN
from MCNN.dataset.data_generator import OxfordFlower, OmniglotDatabase, MiniImagenetDatabase
# from MAML.dataset.data_generator import OxfordFlower, OmniglotDatabase, MiniImagenetDatabase

logging.disable(logging.WARNING)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

if __name__ == '__main__':
    # 학습에 필요한 파라미터를 입력으로 받습니다.
    parser = argparse.ArgumentParser()

    #####################################
    # Configuration Phase
    #####################################
    # (Add) Process Configuration
    parser.add_argument('--mdl_id', type=str, default='M04')       # Default value for testing
    parser.add_argument('--prjt_id', type=str, default='test_mcnn6')     # Default value for testing
    parser.add_argument('--pipeln_id', type=str, default='P43')    # Default value for testing
    parser.add_argument('--data_dir', type=str,  # Default value for testing
                        default='/home/istream3/matrix/apps/tomcat-8.5.39/webapps/bizmdl/metax/prj_data/M04/RAW/oxfordflower')
    parser.add_argument('--prior_dir', type=str,    # Default value for testing
                        default='/home/istream3/matrix/apps/tomcat-8.5.39/webapps/bizmdl/metax/prj_data/M04/P42/test_mcnn4')
    parser.add_argument('--curr_dir', type=str,     # Default value for testing
                        default='/home/istream3/matrix/apps/tomcat-8.5.39/webapps/bizmdl/metax/prj_data/M04/P43/test_mcnn4')

    # Model Configuration
    parser.add_argument('--benchmark_dataset', type=str, default='oxford_flower')
    parser.add_argument('--network_cls', type=str, default='modified_mcnn')

    # -----

    args = parser.parse_args()

    # 3세부 추가
    args.step1_dir = '/home/istream3/matrix/apps/tomcat-8.5.39/webapps/bizmdl/metax/prj_data/M04/P41/test_mcnn4'
    args.step2_dir = args.prior_dir
    args.step3_dir = args.curr_dir
    args.data_path = args.data_dir
    args.base_path = args.curr_dir

    # (Add) set previous step path of initialization
    step_2_ini_path = os.path.join(args.prior_dir, 'step2.ini')
    print(f"Step2 's *.ini file path = {step_2_ini_path}")

    # (Add) Load previous configuration file
    config = ConfigParser()

    # config.read(step_2_ini_path, encoding='utf-8')
    test_path = os.path.join('step2.ini')
    config.read(step_2_ini_path, encoding='utf-8')

    # (Add) Add previous step configuration to current arguments
    def _conv_config_to_dict(prev_conf):
        arg_dict = {}
        for section in prev_conf.sections():
            for key, val in prev_conf[section].items():
                try:
                    ast.literal_eval(val)
                    arg_dict[key] = ast.literal_eval(val)
                # string configuration
                except ValueError:
                    arg_dict[key] = val

        return arg_dict

    prev_args = _conv_config_to_dict(prev_conf=config)

    # (Add) Add argument to configuration file
    step = 'step3'
    config[step] = dict()
    # {
    #     'benchmark_dataset': args.benchmark_dataset,
    #     'network_cls': args.network_cls,
    # }

    database = None
    network_cls = None

    # (Add) Load .pkl file path of previous step
    step_3_pkl = os.path.join(args.prior_dir, 'summary', f"{config['step2']['network_cls']}.pkl")
    step_4_pkl = os.path.join(args.curr_dir, 'summary', f"{config['step2']['network_cls']}.pkl")

    #####################################
    # Test Phase
    #####################################
    # (Add) if database object was saved, then load database pickle
    database = None
    if os.path.isfile(step_3_pkl):
        print("Load dataset")
        with open(step_3_pkl, 'rb') as f:
            database = pickle.load(f)
    else:
        raise FileNotFoundError

    #  # (Add) Save the database file
    os.makedirs(os.path.dirname(step_4_pkl), exist_ok=True)
    with open(step_4_pkl, 'wb') as f:
        pickle.dump(database, f)

    # # 데이터셋 객체를 생성합니다.
    # # 타입 : tf.data.Dataset
    # if args.benchmark_dataset == "omniglot":
    #     database = OmniglotDatabase(
    #         raw_data_address=os.path.join('dataset', 'omniglot'),
    #         random_seed=47,
    #         num_train_classes=1200,
    #         num_val_classes=100)
    # elif args.benchmark_dataset == "mini_imagenet":
    #     database = MiniImagenetDatabase(
    #         raw_data_address=os.path.join('', 'dataset', 'mini_imagenet'),
    #         random_seed=-1)
    # elif args.benchmark_dataset == "oxford_flower":
    #     database = OxfordFlower(
    #         config_path=os.path.join('.', 'dataset', 'raw_data', 'oxfordflower', 'args.ini'),
    #         random_seed=47, use_exist=True)
            
    # 모델 객체를 생성합니다.
    if args.network_cls == "modified_mcnn":
        network_cls = Modified_m_CNN
    # elif args.network_cls == "omniglot":
    #     network_cls = OmniglotModel
    # elif args.network_cls == "mini_imagenet":
    #     network_cls = MiniImagenetModel

    if network_cls in [Modified_m_CNN]:
        prev_args.update(vars(args))
        hetero = Hetero(prev_args, database, network_cls)  # 객체 생성
        # hetero = Hetero(args, os.path.join('.', 'dataset', 'raw_data', 'oxfordflower', 'args.ini'),
        #                 database, network_cls)    # 객체 생성
        loss, acc = hetero.evaluate()    # 훈련된 체크포인트를 받아서 test dataset에서 결과 살핌
        print(f"loss == {loss}")
        print(f"acc == {acc}")
        eval_result = hetero.evaluate_with_demo(acc)    # 그림, 텍스트와 예측 결과를 보여주는 generator

    # elif network_cls in []:
    #     maml = ModelAgnosticMetaLearning(args, database, network_cls)
    #     maml.meta_train(epochs=args.epochs)
