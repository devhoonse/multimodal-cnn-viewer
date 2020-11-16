# path 추가
import sys

sys.path.append('/home/istream3/istream/env/backend/lib/python3.6/site-packages/BIMATRIX/')


from MAML.dataset.data_generator import OmniglotDatabase, MiniImagenetDatabase
import argparse
import logging, os
import pickle
import tqdm
import json
import numpy as np
from configparser import ConfigParser
from MAML.utils import save_nwaykshot

# # 로깅 설정
# logging.disable(logging.WARNING)
# os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"


# 주요 경로 정보들 꺼내오기
mdl_nm: str = 'mini_imagenet'
pwd: str = '/home/istream3/matrix/apps/tomcat-8.5.39/webapps/bizmdl/metax/prj_data/M02/P21'
prior_dat_dir: str = '/home/istream3/matrix/apps/tomcat-8.5.39/webapps/bizmdl/metax/prj_data/M02/P20'
raw_dat_dir: str = '/home/istream3/matrix/apps/tomcat-8.5.39/webapps/bizmdl/metax/prj_data/M02/RAW/mini_imagenet'
prjt_id: str = 'mprj'
n: int = 5
k: int = 3
meta_batch_size: int = 2


# 꺼내온 정보로부터 참조될 경로들 설정하기
save_dir = os.path.join(pwd, prjt_id)  # 스크립트 실행 결과물로 저장될 모든 파일들은 이 폴더에 저장
prior_save_dir = os.path.join(prior_dat_dir, prjt_id)
prepared_db_dir = os.path.join(prior_save_dir, 'fdb')
step1_pkl_path = os.path.join(prior_save_dir, 'summary', f'{mdl_nm}.pkl')
step2_pkl_path = os.path.join(save_dir, 'summary', f'{mdl_nm}.pkl')
step1_args_path = os.path.join(prior_save_dir, 'step1.ini')
step2_args_path = os.path.join(save_dir, 'step2.ini')
nk_json_path = os.path.join(save_dir, 'nwaykshot.json')
nk_fdb_json_path = os.path.join(save_dir, 'nwaykshot_fdb.json')
nk_json_url = nk_json_path.replace('$$was_doc_root_path$$', '$$host_url$$')

# 경로값 확인
print(f"mdl_nm == {mdl_nm}")
print(f"{os.path.exists(raw_dat_dir)} / raw_dat_dir == {raw_dat_dir}")
print(f"{os.path.exists(pwd)} / pwd == {pwd}")
print(f"{os.path.exists(save_dir)} / save_dir == {save_dir}")
print(f"{os.path.exists(prior_dat_dir)} / prior_dat_dir == {prior_dat_dir}")
print(f"{os.path.exists(prior_save_dir)} / prior_save_dir == {prior_save_dir}")
print(f"{os.path.exists(prepared_db_dir)} / prepared_db_dir == {prepared_db_dir}")
print(f"{os.path.exists(step1_pkl_path)} / step1_pkl_path == {step1_pkl_path}")
print(f"{os.path.exists(step2_pkl_path)} / step2_pkl_path == {step2_pkl_path}")
print(f"{os.path.exists(step1_args_path)} / step1_args_path == {step1_args_path}")
print(f"{os.path.exists(step2_args_path)} / step2_args_path == {step2_args_path}")
print(f"{os.path.exists(nk_json_path)} / nk_json_path == {nk_json_path}")
print(f"{os.path.exists(nk_fdb_json_path)} / nk_fdb_json_path == {nk_fdb_json_path}")

# # User Input Argument
# # - n : The number of the sampled class
# # - k : The number of the samples per each class
# # - meta_batch_size : The number of the n-way k-shot tasks in one batch
# parser = argparse.ArgumentParser()

# Config File Load : Step 1 Config file
config_parser = ConfigParser()
# maml_path = os.path.join(os.getcwd(), 'dataset/data/ui_output'.replace('/', os.sep),'maml')
# args_path = os.path.join(maml_path, 'args')
# step1_args_path = os.path.join(args_path, 'step1.ini')
config_parser.read(step1_args_path)
print("Load Step1 arguments from : {}".format(step1_args_path))

# # Config File Writing and save : Step 2 Config file
# parser.add_argument('--benchmark_dataset', type=str, default=config_parser['common_DL']['benchmark_dataset'])       # 20.09.03
# parser.add_argument('--n', type=int, default=5)
# parser.add_argument('--k', type=int, default=3)
# parser.add_argument('--meta_batch_size', type=int, default=2)  # 20.09.03
# args = parser.parse_args()

config_parser['MetaLearning'] = {
    'n': n,
    'k': k,
    'meta_batch_size': meta_batch_size
}

# step2_args_path = os.path.join(args_path, 'step2.ini')
os.makedirs(os.path.dirname(step2_args_path), exist_ok=True)
with open(step2_args_path, 'w') as f:
    config_parser.write(f)
print(f"Step2 args are saved to >> {step2_args_path}")

# # Setup paths
# # 1. Step1's database.pkl path
# base_path_step1 = os.path.join(maml_path, 'step1')
# os.makedirs(base_path_step1, exist_ok=True)

# base_dataset_path_step1 = os.path.join(base_path_step1, args.benchmark_dataset)
# os.makedirs(base_dataset_path_step1, exist_ok=True)
# save_path_step1 = os.path.join(base_dataset_path_step1, '{}.pkl'.format(args.benchmark_dataset))

# # 2. Step2 base path
# base_path_step = os.path.join(maml_path, 'step2')
# os.makedirs(base_path_step, exist_ok=True)

# base_dataset_path = os.path.join(base_path_step, args.benchmark_dataset)
# os.makedirs(base_dataset_path, exist_ok=True)

# save_path = os.path.join(base_dataset_path, '{}.pkl'.format(args.benchmark_dataset))

if os.path.isfile(step1_pkl_path):
    print(f"Loaded dataset from {step1_pkl_path}")
    with open(step1_pkl_path, 'rb') as f:
        database = pickle.load(f)
else:
    # 데이터셋 객체를 생성합니다.
    # 타입 : tf.data.Dataset

    if mdl_nm == "omniglot":
        database = OmniglotDatabase(
            # 200831 changed path, add raw_data folder
            raw_data_address=raw_dat_dir,
            database_address=prepared_db_dir,
            random_seed=47,
            num_train_classes=1200,
            num_val_classes=100,
            is_preview=False)
        print('database loaded')

    # [TODO] Add get_statistic() method to MiniImagenetDatabase class
    elif mdl_nm == "mini_imagenet":  # Tested. OK
        database = MiniImagenetDatabase(
            # 200831 changed path, add raw_data folder
            raw_data_address=raw_dat_dir,
            database_address=prepared_db_dir,
            random_seed=-1,
            is_preview=False)
        print('database loaded')

    # if mdl_nm == "omniglot":
    #     database = OmniglotDatabase(
    #         # 200831 changed path, add raw_data folder
    #         raw_data_address="dataset/raw_data/omniglot".replace('/', os.sep),
    #         random_seed=47,
    #         num_train_classes=1200,
    #         num_val_classes=100)
    # elif mdl_nm == "mini_imagenet":
    #     database=MiniImagenetDatabase(
    #         # 200831 changed path, add raw_data folder
    #         raw_data_address="/dataset/raw_data/mini_imagenet".replace('/', os.sep),
    #         random_seed=-1)

# Save the database file
os.makedirs(os.path.dirname(step2_pkl_path), exist_ok=True)
with open(step2_pkl_path, 'wb') as f:
    pickle.dump(database, f)  # e.g. for omniglot, ./dataset/data/ui_output/maml/step2/omniglot.pkl
# -> To laod this file in the next step


# Saving N-way K-shot JSON for Test dataset

database.is_preview = True
# [TODO] Train folder -> Test folder
test_dataset = database.get_supervised_meta_learning_dataset(
    database.test_folders,
    n = n,
    k = k,
    meta_batch_size = meta_batch_size
)
# print(test_dataset)

# Numbering the classees
train_folders = sorted(database.train_folders)
val_folders = sorted(database.val_folders)
test_folders = sorted(database.test_folders)
print(f"train_folders == {train_folders}")
print(f"val_folders == {val_folders}")
print(f"test_folders == {test_folders}")

folders = train_folders + val_folders + test_folders
folders.sort()
print(f"folders == {folders}")

class2num = {n.split(os.sep)[-1]: 'class{}'.format(i) for i, n in enumerate(folders)}
print(f"class2num == {class2num}")
num2class = {v: k for k, v in class2num.items()}
print(f"num2class == {num2class}")

# Save the N-way K-shot task json file (for tarin set)
# json_save_path = os.path.join(base_dataset_path, 'nwaykshot_{}.json'.format(args.benchmark_dataset))
if mdl_nm == "omniglot":
    save_nwaykshot(test_dataset, nk_fdb_json_path, class2num)
elif mdl_nm == "mini_imagenet":
    save_nwaykshot(test_dataset, nk_fdb_json_path, class2num,
                   prepared_db_dir=raw_dat_dir,
                   change_mini_imagenet_cls_name=True
                   )

# json 에 기록된 이미지 파일 경로에서 WAS Document Root 경로를 HOST_URL 주소로 Replace 하여 재저장
with open(nk_fdb_json_path, 'r') as json_file:
    nk_dict: dict = json.load(json_file)
for task_nm, task_info in nk_dict.items():
    task_supports: dict = task_info['supports']
    task_query: dict = task_info['query']
    for sup_cls_nm, sup_cls_items in task_supports.items():
        for sup_cls_item in sup_cls_items:
            sup_cls_item['path'] = sup_cls_item['path'].replace('$$was_doc_root_path$$', '$$host_url$$')
    for qry_cls_nm, qry_cls_items in task_query.items():
        for qry_cls_item in qry_cls_items:
            qry_cls_item['path'] = qry_cls_item['path'].replace('$$was_doc_root_path$$', '$$host_url$$')

with open(nk_json_path, 'w') as iowrapper:
    json.dump(nk_dict, iowrapper, indent='\t')

print(nk_json_url)