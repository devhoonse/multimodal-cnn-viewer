# path 추가
import json
import sys

sys.path.append('/home/istream3/istream/env/backend/lib/python3.6/site-packages/BIMATRIX/')
sys.path.append('/home/istream3/py_codepad/metax_manager/')

from learner_server.configs import ApplicationConfiguration
from learner_server.dao import ProcessDAO, OracleDataSource, AbstractSession
from learner_server.utils import DateTimeHandler

from MAML.model.optimization_based.maml import OmniglotModel, MiniImagenetModel, ModelAgnosticMetaLearning
from MAML.dataset.data_generator import OmniglotDatabase, MiniImagenetDatabase
import argparse

import logging, os, glob, sys
import pickle
from configparser import ConfigParser


logging.disable(logging.WARNING)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

if __name__ == '__main__':
    # User Input of STEP3
    # 1. epochs : 학습시 전체 데이터셋 반복 횟수
    # 2. network_cls : 메타러닝으로 학습될 모델 기본값 : step2에서 저장된 값
    # 3. meta_learning_rate : Outer loop learning rate
    # 4. meta_batch_size : N of tasks in one meta-batch (2단계에서 저장된 값을 무시하고 재설정가능)
    # 5. num_steps_ml : Training set에 대한 inner loop gradient update step 횟수
    # 6. lr_inner_ml : Inner loop의 learning rate
    # 7. num_steps_validation : Validation set에 대한  inner loop gradient update step 횟수
    # 8. save_after_epochs : 모델 저장 주기(1인 경우 매 epoch마다 저장)
    # 9. report_validation_frequency : validation set에 대한 evaluation 결과 프린트 주기

    # 객체 선언
    parser = argparse.ArgumentParser()
    config_parser = ConfigParser()

    # [3세부 추가] 외부에서 이전 2단계 및 현재 3단계 디렉토리 경로를 직접 받아올 수 있도록 argument 추가
    parser.add_argument('--mdl_id', type=str, default="M01")    # default value for testing
    parser.add_argument('--prjt_id', type=str, default="omniglottest")    # default value for testing
    parser.add_argument('--pipeln_id', type=str, default="P12")    # default value for testing
    parser.add_argument('--prior_dir', type=str,  # default value for testing
                        default='/home/istream3/matrix/apps/tomcat-8.5.39/webapps/bizmdl/metax/prj_data/M01/P11/omniglottest')
    parser.add_argument('--curr_dir', type=str,  # default value for testing
                        default='/home/istream3/matrix/apps/tomcat-8.5.39/webapps/bizmdl/metax/prj_data/M01/P12/omniglottest')

    # 빠른 테스트를 위한 세팅
    # Argument for Common Deep Learning
    # It take user input & It also have default values
    parser.add_argument('--epochs', type=int, default=20)  # User Input STEP3
    parser.add_argument('--meta_learning_rate', type=float, default=0.001)  # User Input STEP3

    # Argument for Meta-Learning
    # It take user input & It also have default values
    parser.add_argument('--meta_batch_size', type=int, default=2)  # User Input STEP3
    parser.add_argument('--num_steps_ml', type=int, default=1)  # User Input STEP3
    parser.add_argument('--lr_inner_ml', type=float, default=0.4)  # User Input STEP3
    parser.add_argument('--iterations', type=int, default=1)
    parser.add_argument('--num_steps_validation', type=int, default=1)  # User Input STEP3
    # --iterations : STEP3 에서 사용되진 않지만 다음 스텝에서 모델로드시 변수가 존재해야 하므로 임의값 할당

    # Argument for wrting log & save file
    # It take user input & It also have default values
    parser.add_argument('--save_after_epochs', type=int, default=1)  # User Input STEP3
    parser.add_argument('--report_validation_frequency', type=int, default=1)  # User Input STEP3
    parser.add_argument('--log_train_images_after_iteration', type=int, default=-1)  # No Record

    # read argument settings from cmdline
    args = parser.parse_args()

    # [3세부 추가] 이전 2단계 디렉토리 안에서 step2.ini 파일 경로 설정
    step2_ini_path: str = os.path.join(args.prior_dir, 'step2.ini')

    # [3세부 추가] 이전 단계에서 저장된 .ini 설정파일 읽어오기
    print(f"step02 's *.ini file path = {step2_ini_path}")
    config_parser.read(step2_ini_path)

    # [3세부 추가] 명령행을 통해 받지 않지만 필요한 매개변수들은 NameSpace 객체에 직접 등록
    args.benchmark_dataset = config_parser['common_DL']['benchmark_dataset']
    args.network_cls = config_parser['common_DL']['benchmark_dataset']
    args.n = int(config_parser['MetaLearning']['n'])
    args.k = int(config_parser['MetaLearning']['k'])

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
        # 'iterations': args.iterations,
        'num_steps_validation': args.num_steps_validation,
    }
    config_parser['LogSave'] = {
        'save_after_epochs': args.save_after_epochs,
        'report_validation_frequency': args.report_validation_frequency,
        'log_train_images_after_iteration': args.log_train_images_after_iteration,
    }


    def _get_config_info(args):
        return f'model-{config_parser["common_DL"]["benchmark_dataset"]}_' \
               f'mbs-{args.meta_batch_size}_' \
               f'n-{config_parser["MetaLearning"]["n"]}_' \
               f'k-{config_parser["MetaLearning"]["k"]}_' \
               f'stp-{args.num_steps_ml}'


    step3_args_path = os.path.join(args.curr_dir, 'step3_{}.ini'.format(_get_config_info(args)))
    os.makedirs(args.curr_dir, exist_ok=True)
    with open(step3_args_path, 'w') as f:
        config_parser.write(f)
    print("Step3 args are saved")

    # [3세부 추가] 이전 2단계 .pkl file path
    step2_pkl: str = os.path.join(args.prior_dir, 'summary',
                                  f"{config_parser['common_DL']['benchmark_dataset']}.pkl")
    step3_pkl: str = os.path.join(args.curr_dir, 'summary',
                                  f"{config_parser['common_DL']['benchmark_dataset']}.pkl")

    database = None
    if os.path.isfile(step2_pkl):
        print("Load dataset")
        with open(step2_pkl, 'rb') as f:
            database = pickle.load(f)
    else:  # [3세부 추가] UI 단에서부터 이전 단계를 실행하지 않은 경우에는 요청조차 보낼 수 없기 때문에 이 분기로 올 수 없음.
        raise FileNotFoundError

    # Save the database file
    os.makedirs(os.path.dirname(step3_pkl), exist_ok=True)
    with open(step3_pkl, 'wb') as f:
        pickle.dump(database, f)  # e.g. for omniglot, ./dataset/data/ui_output/maml/step1/omniglot.pkl
    # -> To load this file in the next step

    # 모델 객체를 생성합니다.
    network_cls: type
    if config_parser["common_DL"]["benchmark_dataset"] == "omniglot":
        network_cls = OmniglotModel
    elif config_parser["common_DL"]["benchmark_dataset"] == "mini_imagenet":
        network_cls = MiniImagenetModel

    # [3세부 추가] for debugging
    print(args, flush=True)

    # 학습을 위한 클래스를 생성합니다.
    maml = ModelAgnosticMetaLearning(args, database, network_cls, args.curr_dir)
    # args : 파라미터      type : parser.parse_args
    # database : 데이터셋  type : database
    # network_cls : 모델   type : MetaLearning

    # 학습을 위한 클래스를 사용하여 입력받은 파라미터를 통해 meta_train을 수행합니다.
    maml.meta_train(epochs=args.epochs)
    # epochs : 반복 횟수 type : int

    # [3세부 추가] UI 상에서 참조해야 할 항목들의 경로 값을 담은 json 파일 저장
    def _get_model_name(args):
        return f'model-{network_cls.__name__}_' \
               f'mbs-{args.meta_batch_size}_' \
               f'n-{config_parser["MetaLearning"]["n"]}_' \
               f'k-{config_parser["MetaLearning"]["k"]}_' \
               f'stp-{args.num_steps_ml}'
    model_name: str = _get_model_name(args)
    model_path: str = os.path.join(args.curr_dir, model_name)
    train_csv_path: str = os.path.join(model_path, 'train', 'train.csv')
    validation_csv_path: str = os.path.join(model_path, 'val', 'val.csv')
    ui_src_info_path: str = os.path.join(args.curr_dir, 'ui_src.json')
    with open(ui_src_info_path, 'w') as iowrapper:
        json.dump(
            {"train_csv_path": train_csv_path, "validation_csv_path": validation_csv_path},
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
