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
# from MAML.dataset.data_generator import OxfordFlower, OmniglotDatabase, MiniImagenetDatabase


logging.disable(logging.WARNING)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

if __name__ == '__main__':
    # 학습에 필요한 파라미터를 입력으로 받습니다.
    parser = argparse.ArgumentParser()

    #######################
    # Configuration Phase
    #######################
    # (Add) Process Configuration
    parser.add_argument('--mdl_id', type=str, default='M04')       # Default value for testing
    parser.add_argument('--prjt_id', type=str, default='test_mcnn2')     # Default value for testing
    parser.add_argument('--pipeln_id', type=str, default='P42')    # Default value for testing
    parser.add_argument('--data_dir', type=str,    # Default value for testing
                        default='/home/istream3/matrix/apps/tomcat-8.5.39/webapps/bizmdl/metax/prj_data/M04/RAW/oxfordflower')
    parser.add_argument('--prior_dir', type=str,    # Default value for testing
                        default='/home/istream3/matrix/apps/tomcat-8.5.39/webapps/bizmdl/metax/prj_data/M04/P41/test_mcnn2')
    parser.add_argument('--curr_dir', type=str,     # Default value for testing
                        default='/home/istream3/matrix/apps/tomcat-8.5.39/webapps/bizmdl/metax/prj_data/M04/P42/test_mcnn2')

    # Model Configuration
    parser.add_argument('--benchmark_dataset', type=str, default='oxford_flower')
    parser.add_argument('--network_cls', type=str, default='modified_mcnn')
    parser.add_argument('--epochs', type=int, default=3)
    parser.add_argument("--epochs2", type=int, default=3)         # image encoder를 pretrain 시킬 때 epochs
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument("--batch_size2", type=int, default=64)    # image encoder를 pretrain 시킬 때 batch_size
    parser.add_argument("--encoder_name", type=str, default="MobileNetV2")
    parser.add_argument("--optimizer", type=str, default="SGD")
    parser.add_argument("--drop_out", type=float, default=0.4)
    parser.add_argument("--drop_out2", type=float, default=0.4)
    parser.add_argument("--filter_sizes", type=str, default="2,3,4")
    parser.add_argument("--num_filters", type=float, default=256)
    parser.add_argument("--lambda", type=float, default=0.05)
    parser.add_argument("--lr", type=float, default=0.005)
    parser.add_argument("--clip_norm", type=float, default=.0)
    parser.add_argument("--binary", action="store_true")      # is binary classification?
    parser.add_argument("--pretrain", action="store_true")    # Use pretrain or not
    parser.add_argument("--finetune", action="store_true")
    parser.add_argument("--seed", type=int, default=1234)   # random seed

    args = parser.parse_args()

    # 3세부 추가
    args.step1_dir = args.prior_dir
    args.step2_dir = args.curr_dir

    # (Add) set previous step path of initialization
    step_2_ini_path = os.path.join(args.prior_dir, 'step1.ini')
    print(f"Step2 's *.ini file path = {step_2_ini_path}")

    # (Add) Load previous configuration file
    config = ConfigParser()

    # config.read(step_2_ini_path, encoding='utf-8')
    test_path = os.path.join('step2.ini')
    config.read(step_2_ini_path)    # , encoding='utf-8'

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
    # prev_args.update(vars(args))

    # (Add) Add argument to configuration file
    step = 'step2'
    config[step] = {
        'benchmark_dataset': args.benchmark_dataset,
        'network_cls': args.network_cls,
        'epochs': args.epochs,
        'epochs2': args.epochs2,
        'batch_size': args.batch_size,
        'batch_size2': args.batch_size2,
        'encoder_name': args.encoder_name,
        'optimizer': args.optimizer,
        'drop_out': args.drop_out,
        'drop_out2': args.drop_out2,
        'lr': args.lr,
        'clip_norm': args.clip_norm,
        'lambda': args.__getattribute__('lambda'),
        'filter_sizes': args.filter_sizes,
        'num_filters': args.num_filters,
        'binary': args.binary,
        'pretrain': args.pretrain,
        'finetune': args.finetune
    }

    # def _get_config_info(args):
    #     return f'model-{config["step_3"]["benchmark_dataset"]}'

    # (Add) Save step 3 config file
    step_3_args_path = os.path.join(args.curr_dir, step + '.ini')
    os.makedirs(args.curr_dir, exist_ok=True)
    with open(step_3_args_path, 'w') as f:
        config.write(f)
    print("Step 3 arguments are saved")

    # (Add) Load .pkl file path of previous step
    step_2_pkl = os.path.join(args.prior_dir, 'summary', f"{config[step]['network_cls']}.pkl")
    step_3_pkl = os.path.join(args.curr_dir, 'summary', f"{config[step]['network_cls']}.pkl")

    #####################################
    # Test Phase
    #####################################
    # (Add) if database object was saved, then load database pickle
    database = None
    if os.path.isfile(step_2_pkl):
        print("Load dataset")
        with open(step_2_pkl, 'rb') as f:
            database = pickle.load(f)
    else:
        raise FileNotFoundError

    #  # (Add) Save the database file
    os.makedirs(os.path.dirname(step_3_pkl), exist_ok=True)
    with open(step_3_pkl, 'wb') as f:
        pickle.dump(database, f)

    # if config[step]['benchmark_dataset'] == "oxford_flower":
    #     # path_conf = os.path.join('.', 'dataset', 'raw_data', 'oxfordflower', 'args.ini')
    #     database = OxfordFlower(
    #         step=step,
    #         config=config,
    #         base_path=args.curr_path,
    #         data_path=args.curr_path,
    #         save_path='',
    #         is_preview=False)
    #
    # elif args.benchmark_dataset == "omniglot":
    #     database = OmniglotDatabase(
    #         raw_data_address=os.path.join('dataset', 'omniglot'),
    #         random_seed=47,
    #         num_train_classes=1200,
    #         num_val_classes=100)
    #
    # elif args.benchmark_dataset == "mini_imagenet":
    #     database = MiniImagenetDatabase(
    #         raw_data_address=os.path.join('', 'dataset', 'mini_imagenet'),
    #         random_seed=-1)
            
    # 모델 객체를 생성합니다.
    network_cls = None
    if args.network_cls == "modified_mcnn":
        network_cls = Modified_m_CNN
    # elif args.network_cls == "omniglot":
    #     network_cls=OmniglotModel
    # elif args.network_cls == "mini_imagenet":
    #     network_cls=MiniImagenetModel

    if args.network_cls in ["modified_mcnn"]:
        # path_conf = os.path.join('.', 'dataset', 'raw_data', 'oxfordflower', 'args.ini')
        # update_config(args, "model", path_conf)
        prev_args.update(vars(args))
        hetero = Hetero(args=prev_args, database=database, network_cls=network_cls)
        hetero.train()

        # (Add) Save log path information to json
        log_path = os.path.join(args.step2_dir, 'model', 'hetero', 'model_log', 'train_csv', 'log.csv')
        ui_src_info_path = os.path.join(args.curr_dir, 'ui_src.json')
        with open(ui_src_info_path, 'w') as iowrapper:
            json.dump(
                {
                    "train_csv_path": hetero.path_log.replace('.csv', '_train.csv'),
                    "validation_csv_path": hetero.path_log.replace('.csv', '_val.csv')
                },
                iowrapper,
                indent='\t'
            )

        # (Add) Process of saving log on DB
        config_db = ApplicationConfiguration.instance()
        config_db.init('config.properties')
        data_source = OracleDataSource.instance()
        data_source.init(config_db)
        session: AbstractSession = data_source.get_session()
        ProcessDAO.finish_subprocess(session,
                                     END_DT_TM=DateTimeHandler.get_current_time_str(),
                                     MDL_ID=args.mdl_id,
                                     PRJT_ID=args.prjt_id,
                                     PIPELN_ID=args.pipeln_id)
        session.close()
        data_source.close()

        print("finished")   # 3세부 추가 : for notifying end of the script
    # elif args.network_cls in ["OmniglotModel", "MiniImagenetModel"]:
    #     maml = ModelAgnosticMetaLearning(args, database, network_cls)
    #     maml.meta_train(epochs=args.epochs)
