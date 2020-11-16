# 일시적 path 추가
import json
import sys

sys.path.append('/home/istream3/istream/env/backend/lib/python3.6/site-packages/BIMATRIX/')
sys.path.append('/home/istream3/py_codepad/metax_manager/')

from learner_server.configs import ApplicationConfiguration
from learner_server.dao import OracleDataSource, AbstractSession, ProcessDAO
from learner_server.utils import DateTimeHandler

from MAML.model.optimization_based.maml import OmniglotModel, MiniImagenetModel, ModelAgnosticMetaLearning
from MAML.dataset.data_generator import OmniglotDatabase, MiniImagenetDatabase
import argparse

import logging, os
import pickle
import glob
from configparser import ConfigParser
from pathlib import Path

logging.disable(logging.WARNING)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"


if __name__ == '__main__':
    # No User Input of STEP5

    # 객체 선언
    parser = argparse.ArgumentParser()
    config_parser = ConfigParser()

    # Load latest step4_{config}.ini

    # [3세부 추가] 외부에서 이전 4단계 및 현재 5단계 디렉토리 경로를 직접 받아올 수 있도록 argument 추가
    parser.add_argument('--mdl_id', type=str, default="M01")  # default value for testing
    parser.add_argument('--prjt_id', type=str, default="omniglottest")  # default value for testing
    parser.add_argument('--pipeln_id', type=str, default="P12")  # default value for testing
    parser.add_argument('--step2_dir', type=str,  # default value for testing
                        default='/home/istream3/matrix/apps/tomcat-8.5.39/webapps/bizmdl/metax/prj_data/M01/P11/omniglottest')
    parser.add_argument('--prior_dir', type=str,  # default value for testing
                        default='/home/istream3/matrix/apps/tomcat-8.5.39/webapps/bizmdl/metax/prj_data/M01/P13/omniglottest')
    parser.add_argument('--curr_dir', type=str,  # default value for testing
                        default='/home/istream3/matrix/apps/tomcat-8.5.39/webapps/bizmdl/metax/prj_data/M01/P14/omniglottest')

    # Argument for Common Deep Learning
    # It take user input & It also have default values
    parser.add_argument('--epochs', type=int, default=20)
    parser.add_argument('--meta_learning_rate', type=float, default=0.001)

    # Argument for Meta-Learning
    # It take user input & It also have default values
    parser.add_argument('--n', type=int, default=5)
    parser.add_argument('--k', type=int, default=3)
    parser.add_argument('--meta_batch_size', type=int, default=7)
    parser.add_argument('--num_steps_ml', type=int, default=10)  # User Input of STEP4
    parser.add_argument('--lr_inner_ml', type=float, default=0.4)
    parser.add_argument('--iterations', type=int, default=10)  # User Input of STEP4
    parser.add_argument('--num_steps_validation', type=int, default=10)  # User Input of STEP4

    # Argument for wrting log & save file
    # It take user input & It also have default values
    parser.add_argument('--save_after_epochs', type=int, default=1)
    parser.add_argument('--report_validation_frequency', type=int, default=50)
    parser.add_argument('--log_train_images_after_iteration', type=int, default=-1)

    # read argument settings from cmdline
    args = parser.parse_args()

    # [3세부 추가] 이전 4단계 디렉토리 안에서 .ini 파일 경로 설정
    step4_ini_path = [path for path in Path(args.prior_dir).rglob('*.ini')]
    if len(step4_ini_path) == 0:
        raise FileNotFoundError
    step4_ini_path = step4_ini_path[0]

    # [3세부 추가] 이전 단계에서 저장된 .ini 설정파일 읽어오기
    print(f"step04 's *.ini file path = {step4_ini_path}")
    config_parser.read(step4_ini_path)

    # [3세부 추가] 명령행을 통해 받지 않지만 필요한 매개변수들은 이전 단계 설정으로부터 NameSpace 객체에 직접 등록
    args.benchmark_dataset = config_parser['common_DL']['benchmark_dataset']
    args.network_cls = config_parser['common_DL']['benchmark_dataset']
    args.epochs = int(config_parser['common_DL']['epochs'])
    args.meta_learning_rate = float(config_parser['common_DL']['meta_learning_rate'])
    args.n = int(config_parser['MetaLearning']['n'])
    args.k = int(config_parser['MetaLearning']['k'])
    args.meta_batch_size = int(config_parser['MetaLearning']['meta_batch_size'])
    args.num_steps_ml = int(config_parser['MetaLearning']['num_steps_ml'])
    args.lr_inner_ml = float(config_parser['MetaLearning']['lr_inner_ml'])
    args.iterations = int(config_parser['MetaLearning']['iterations'])
    args.num_steps_validation = int(config_parser['MetaLearning']['num_steps_validation'])
    args.save_after_epochs = int(config_parser['LogSave']['save_after_epochs'])
    args.report_validation_frequency = int(config_parser['LogSave']['report_validation_frequency'])
    args.log_train_images_after_iteration = int(config_parser['LogSave']['log_train_images_after_iteration'])

    # Create config file
    config_parser['common_DL'] = {
        'benchmark_dataset': args.benchmark_dataset,
        'network_cls': args.network_cls,
        'epochs': args.epochs,
        'meta_learning_rate': args.meta_learning_rate,
    }
    config_parser['MetaLearning'] = {
        'n': args.n,
        'k': args.k,
        'meta_batch_size': args.meta_batch_size,
        'num_steps_ml': args.num_steps_ml,
        'lr_inner_ml': args.lr_inner_ml,
        'iterations': args.iterations,
        'num_steps_validation': args.num_steps_validation,
    }
    config_parser['LogSave'] = {
        'save_after_epochs': args.save_after_epochs,
        'report_validation_frequency': args.report_validation_frequency,
        'log_train_images_after_iteration': args.log_train_images_after_iteration,
    }


    def _get_config_info(args):
        return f'model-{args.network_cls}_' \
               f'mbs-{args.meta_batch_size}_' \
               f'n-{args.n}_' \
               f'k-{args.k}_' \
               f'stp-{args.num_steps_ml}'


    step5_args_path = os.path.join(args.curr_dir, 'step5_{}.ini'.format(_get_config_info(args)))
    os.makedirs(args.curr_dir, exist_ok=True)
    with open(step5_args_path, 'w') as f:
        config_parser.write(f)
    print("Step5 args are saved")

    # [3세부 추가] 이전 2단계 .json, .pkl file path
    step2_pkl: str = os.path.join(args.prior_dir, 'summary',
                                  f"{config_parser['common_DL']['benchmark_dataset']}.pkl")
    step5_pkl: str = os.path.join(args.curr_dir, 'summary',
                                  f"{config_parser['common_DL']['benchmark_dataset']}.pkl")

    # args_path = os.path.join(maml_path, 'args')
    # step4_args_path = os.path.join(args_path, 'step4_{}.ini'.format(_get_config_info(args)))
    # with open(step4_args_path, 'w') as f:
    #     config_parser.write(f)
    # print("Step4 args are saved")

    database = None
    if os.path.isfile(step2_pkl):
        print("Load dataset")
        with open(step2_pkl, 'rb') as f:
            database = pickle.load(f)
    else:   # [3세부 추가]이전 단계를 실행하지 않은 경우에는 UI 단에서부터 요청조차 보낼 수 없기 때문에 이 분기로 올 수 없음.
        raise FileNotFoundError

    # Save the database file
    os.makedirs(os.path.dirname(step5_pkl), exist_ok=True)
    with open(step5_pkl, 'wb') as f:
        pickle.dump(database, f)  # e.g. for omniglot, ./dataset/data/ui_output/maml/step1/omniglot.pkl
    # -> To load this file in the next step

    # 모델 객체를 생성합니다.
    network_cls = None
    if config_parser["common_DL"]["benchmark_dataset"] == "omniglot":
        network_cls = OmniglotModel
    elif config_parser["common_DL"]["benchmark_dataset"] == "mini_imagenet":
        network_cls = MiniImagenetModel

    # 학습을 위한 클래스를 생성합니다.
    maml = ModelAgnosticMetaLearning(args, database, network_cls, args.curr_dir)
    # args : 파라미터      type : parser.parse_args
    # database : 데이터셋  type : database
    # network_cls : 모델   type : MetaLearning

    # 입력받은 파라미터를 통해 해당 epochs의 저장된 모델을 불러옵니다.
    # epochs : 몇번 학습한 모델을 불러올 지  type : int
    # None일 시 최종 학습한 모델을 불러옵니다.

    # 모델 불러오기 위해 checkpoint의 경로를 step4의 경로로 변경
    step4_ckpt_dir = [walk[0] for walk in os.walk(args.prior_dir)
                      if os.path.basename(walk[0]) == 'saved_models']
    if len(step4_ckpt_dir) == 0:
        raise FileNotFoundError
    step4_ckpt_dir = step4_ckpt_dir[0]
    maml.checkpoint_dir = step4_ckpt_dir
    print(maml.checkpoint_dir)

    # [3세부 추가] step2 에서 저장된 nwaykshot.json 경로 확인
    save_path_json_step2: str = os.path.join(args.step2_dir, 'nwaykshot_fdb.json')
    if not os.path.isfile(save_path_json_step2):
        raise FileNotFoundError

    # # meta_test 시 입력받은 파라미터를 통해 fine turning할 횟수 만큼 수행합니다.
    # maml.meta_test(iterations = args.iterations)
    # # iterations : inner loop의 gradient update 횟수 type : int

    # 예측한 결과를 보여줍니다.
    # maml.predict_with_support(save_path=args.curr_dir, meta_test_path=os.path.join('dataset','data','mini_imagenet','test'))
    # meta_test_path 예측할 데이터의 경로               type : string
    # epochs_to_load_from 몇번 학습한 모델을 볼러올지   type : int  None일 시 최종 학습한 모델을 불러옵니다.
    # iterations fine turning 횟수                    type : int
    # print(base_dataset_path)
    # print(save_path_json_step2)
    maml.meta_predict(save_path=args.curr_dir, step2_task_json_path=save_path_json_step2)

    # [3세부 추가] UI 상에서 참조해야 할 항목들의 경로 값을 담은 json 파일 저장
    def _get_model_name(args):
        return f'model-{network_cls.__name__}_' \
               f'mbs-{args.meta_batch_size}_' \
               f'n-{config_parser["MetaLearning"]["n"]}_' \
               f'k-{config_parser["MetaLearning"]["k"]}_' \
               f'stp-{args.num_steps_ml}'
    model_name: str = _get_model_name(args)
    model_path: str = os.path.join(args.curr_dir, model_name)
    prediction_json_path: str = os.path.join(model_path, 'output', f'nwaykshot_{args.benchmark_dataset}.json')
    ui_src_info_path: str = os.path.join(args.curr_dir, 'ui_src.json')
    with open(ui_src_info_path, 'w') as iowrapper:
        json.dump(
            {"prediction_json_path": prediction_json_path},
            iowrapper, indent='\t'
        )

    # [3세부 추가] D/B 내 이력 테이블에 완료 로깅 처리
    config = ApplicationConfiguration.instance()
    config.init('config.properties')
    data_source = OracleDataSource.instance()  # Todo: Make Available Various Types of Data Sources
    data_source.init(config)
    session: AbstractSession = data_source.get_session()
    ProcessDAO.finish_subprocess(session,
                                 END_DT_TM=DateTimeHandler.get_current_time_str(),
                                 MDL_ID=args.mdl_id,
                                 PRJT_ID=args.prjt_id,
                                 PIPELN_ID=args.pipeln_id)
    session.close()
    data_source.close()

    print("debug point")
