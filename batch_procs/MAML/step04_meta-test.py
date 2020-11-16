from MAML.model.optimization_based.maml import OmniglotModel, MiniImagenetModel, ModelAgnosticMetaLearning
from MAML.dataset.data_generator import OmniglotDatabase, MiniImagenetDatabase
import argparse

import logging, os
import pickle
import glob
from configparser import ConfigParser
from pathlib import Path

# 로깅 설정
logging.disable(logging.WARNING)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# 주요 경로 정보들 꺼내오기
mdl_nm: str = mdl_info.iloc[0]['MDL_NM']
pwd: str = work_dir.iloc[0]['DATA_PATH']
prior_dat_dir: str = prior_work_dir.iloc[0]['DATA_PATH']
step2_dat_dir: str = step2_dir.iloc[0]['DATA_PATH']

# 꺼내온 정보로부터 참조될 경로들 설정하기
save_dir = os.path.join(pwd, '$$prjt_id$$')
prior_save_dir = os.path.join(prior_dat_dir, '$$prjt_id$$')
prior_ckpt_dir = [walk[0] for walk in os.walk(prior_save_dir) 
                  if os.path.basename(walk[0]) == 'saved_models']
if len(prior_ckpt_dir) == 0:
    raise FileNotFoundError
prior_ckpt_dir = prior_ckpt_dir[0]
step2_save_dir = os.path.join(step2_dat_dir, '$$prjt_id$$')
step2_pkl_path = os.path.join(step2_save_dir, 'summary', f"{mdl_nm}.pkl")
step4_pkl_path = os.path.join(save_dir, 'summary', f"{mdl_nm}.pkl")
step3_args_path = [path for path in Path(prior_save_dir).rglob('*.ini')]
if len(step3_args_path) == 0:
    raise FileNotFoundError
step3_args_path = step3_args_path[0]
step4_args_path = ''

# 경로값 확인
print(f"mdl_nm == {mdl_nm}")
print(f"{os.path.exists(pwd)} / pwd == {pwd}")
print(f"{os.path.exists(save_dir)} / save_dir == {save_dir}")
print(f"{os.path.exists(prior_dat_dir)} / prior_dat_dir == {prior_dat_dir}")
print(f"{os.path.exists(prior_save_dir)} / prior_save_dir == {prior_save_dir}")
print(f"{os.path.exists(prior_ckpt_dir)} / prior_ckpt_dir == {prior_ckpt_dir}")
print(f"{os.path.exists(step2_dat_dir)} / step2_dat_dir == {step2_dat_dir}")
print(f"{os.path.exists(step2_save_dir)} / step2_save_dir == {step2_save_dir}")
print(f"{os.path.exists(step2_pkl_path)} / step2_pkl_path == {step2_pkl_path}")
print(f"{os.path.exists(step3_args_path)} / step3_args_path == {step3_args_path}")


# User Input of STEP4 
# The default values are the values of step3
# 1. iterations : Test set에 대한 inner loop gradient update steps 횟수(기본값 : num_steps_ml)
# Other arguments are loaded from args_###.ini file that has saved in the step3

# .ini 파일 내 기록된 설정 값 Parser 객체 선언
config_parser = ConfigParser()

# Load latest step3_{config}.ini
config_parser.read(step3_args_path)

# # 학습에 필요한 인자를 입력으로 받습니다.
# # 아래 인자들은 메타러닝 세팅에 대한 것으로 일반 학습에 대한 세팅은 다를 수 있습니다.

# [3세부 추가] 파싱 결과를 담은 NameSpace 객체 받기  
# (i-STREAM 데몬에 전달된 string 커맨드 실행 시
#  parse_args() 메서드 사용 불가, 하여 직접 Namespace 객체를 만들어줌 )
args = argparse.Namespace()
args.benchmark_dataset = config_parser['common_DL']['benchmark_dataset']
args.network_cls = config_parser['common_DL']['benchmark_dataset']
args.epochs = int(config_parser['common_DL']['epochs'])
args.meta_learning_rate = float(config_parser['common_DL']['meta_learning_rate'])
args.n = int(config_parser['MetaLearning']['n'])
args.k = int(config_parser['MetaLearning']['k'])
args.meta_batch_size = int(config_parser['MetaLearning']['meta_batch_size'])
args.num_steps_ml = int(config_parser['MetaLearning']['num_steps_ml'])
args.lr_inner_ml = float(config_parser['MetaLearning']['lr_inner_ml'])
args.iterations = int(config_parser['MetaLearning']['num_steps_ml'])
args.num_steps_validation = int(config_parser['MetaLearning']['num_steps_validation'])
args.save_after_epochs = int(config_parser['LogSave']['save_after_epochs'])
args.report_validation_frequency = int(config_parser['LogSave']['report_validation_frequency'])
args.log_train_images_after_iteration = int(config_parser['LogSave']['log_train_images_after_iteration'])


# [3세부 추가] 요청 폼에 있는 유저 설정 값이
# 기본 값(이전 단계 설정 값)과 다를 경우
# 요청 폼에 있는 유저 설정값으로 args.iterations 값을 대체
if $$iterations$$ != args.iterations:
    args.iterations = $$iterations$$
    print(f"args.iterations has been changed to {$$iterations$$}")

print(args) # for testing

# Create config file
config_parser['common_DL'] = {
    'benchmark_dataset' : args.benchmark_dataset,
    'network_cls' : args.network_cls,
    'epochs' : args.epochs,
    'meta_learning_rate' : args.meta_learning_rate,
}

config_parser['MetaLearning'] = {
    'n' : args.n,
    'k' : args.k,
    'meta_batch_size' : args.meta_batch_size,
    'num_steps_ml' : args.num_steps_ml,
    'lr_inner_ml' : args.lr_inner_ml,
    'iterations' : args.iterations,
    'num_steps_validation' : args.num_steps_validation,
}

config_parser['LogSave'] = {
    'save_after_epochs' : args.save_after_epochs,
    'report_validation_frequency' : args.report_validation_frequency,
    'log_train_images_after_iteration' : args.log_train_images_after_iteration,
}


def _get_config_info(args):
    return f'model-{args.network_cls}_' \
        f'mbs-{args.meta_batch_size}_' \
        f'n-{args.n}_' \
        f'k-{args.k}_' \
        f'stp-{args.num_steps_ml}'
# args_path = os.path.join(maml_path, 'args')
step4_args_path = os.path.join(save_dir, 'step4_{}.ini'.format(_get_config_info(args)))
print(f"{os.path.exists(step4_args_path)} / step4_args_path == {step4_args_path}")
os.makedirs(save_dir, exist_ok=True)
with open(step4_args_path, 'w') as f:
    config_parser.write(f)
print(f"Step4 args are saved to > {step4_args_path}")

# # Setup paths
# # 1. Step2's database.pkl path

# base_path_step2 = os.path.join(maml_path, 'step2')
# os.makedirs(base_path_step2, exist_ok=True)
# base_dataset_path_step2 = os.path.join(base_path_step2, args.benchmark_dataset)
# os.makedirs(base_dataset_path_step2, exist_ok=True)
# save_path_step2 = os.path.join(base_dataset_path_step2, '{}.pkl'.format(args.benchmark_dataset))

# # 2. Step3's path : to load the model
# base_path_step3 = os.path.join(maml_path, 'step3')
# base_dataset_path_step3 = os.path.join(base_path_step3, args.benchmark_dataset)

# # 3. Step4 base path
# base_path_step = os.path.join(maml_path, 'step4')
# os.makedirs(base_path_step, exist_ok=True)

# base_dataset_path = os.path.join(base_path_step, args.benchmark_dataset)
# os.makedirs(base_dataset_path, exist_ok=True)

if os.path.isfile(step2_pkl_path):
    print(f"Load dataset from <- {step2_pkl_path}")
    with open(step2_pkl_path, 'rb') as f:
        database = pickle.load(f)
else:   # [3세부 주석] UI 수준에서 이전 단계가 정상적으로 실행되지 않으면 요청이 오지 못하도록 제어하고 있음
    # 데이터셋 객체를 생성합니다.
    # 타입 : tf.data.Dataset
    if args.benchmark_dataset == "omniglot":
        database = OmniglotDatabase(
            # 200831 changed path, add raw_data folder
            raw_data_address="dataset/raw_data/omniglot",
            random_seed=47,
            num_train_classes=1200,
            num_val_classes=100)

    elif args.benchmark_dataset == "mini_imagenet":
        database=MiniImagenetDatabase(
            # 200831 changed path, add raw_data folder
            raw_data_address="dataset/raw_data/mini_imagenet",
            random_seed=-1)

# Save the database file
os.makedirs(os.path.dirname(step4_pkl_path), exist_ok=True)
with open(step4_pkl_path, 'wb') as f:
    pickle.dump(database, f) # e.g. for omniglot, ./dataset/data/ui_output/maml/step1/omniglot.pkl
# -> To laod this file in the next step

# 모델 객체를 생성합니다.
if mdl_nm == "omniglot":
    network_cls = OmniglotModel
elif mdl_nm == "mini_imagenet":
    network_cls = MiniImagenetModel
print(f"network_cls = {network_cls}")      # for testing

# 학습을 위한 클래스를 생성합니다.
maml = ModelAgnosticMetaLearning(args, database, network_cls, save_dir)
print(maml)     # for testing
# args : 파라미터      type : argparse.Namespace [3세부 수정]
# database : 데이터셋  type : database
# network_cls : 모델   type : MetaLearning

# 입력받은 파라미터를 통해 해당 epochs의 저장된 모델을 불러옵니다.
# epochs : 몇번 학습한 모델을 불러올 지  type : int
# None일 시 최종 학습한 모델을 불러옵니다.

# 모델 불러오기 위해 checkpoint의 경로를 step3의 경로로 변경
maml.checkpoint_dir = prior_ckpt_dir

# epoch_count = maml.load_model(epochs = args.epochs)
# print("Load the {}th epoch model".format(epoch_count))

# meta_test 시 입력받은 파라미터를 통해 fine turning할 횟수 만큼 수행합니다.
maml.meta_test(iterations = args.iterations)
# iterations : inner loop의 gradient update 횟수 type : int