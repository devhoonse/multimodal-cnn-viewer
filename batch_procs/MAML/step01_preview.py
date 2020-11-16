from MAML.dataset.data_generator import OmniglotDatabase, MiniImagenetDatabase
import argparse
import logging, os
import pickle
import json
from configparser import ConfigParser

# 세팅된 라이브러리 import 결과 확인
print(__name__)
print(OmniglotDatabase)
print(MiniImagenetDatabase)

# get config parser
config = ConfigParser()

# 로깅 설정
logging.disable(logging.WARNING)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"


# 주요 경로 정보들 꺼내오기
pwd: str = work_dir.iloc[0]['DATA_PATH']    # 현재 실행되는 과제 고유 폴더 위치
mdl_nm: str = mdl_info.iloc[0]['MDL_NM'] # 기준정보 테이블에 기록되어 있는 모델명에 접근
raw_dat_dir: str = raw_data_dir.iloc[0]['DATA_PATH']    # 

# 꺼내온 정보로부터 참조될 경로들 설정하기
save_dir = os.path.join(pwd, '$$prjt_id$$')     # 스크립트 실행 결과물로 저장될 모든 파일들은 이 폴더에 저장
prepared_db_dir = os.path.join(save_dir, 'fdb')
step1_args_path = os.path.join(save_dir, 'step1.ini')
summary_path = os.path.join(save_dir, 'summary')
pkl_path = os.path.join(summary_path, '{}.pkl'.format(mdl_nm))
test_sample_json = os.path.join(summary_path, 'path_sample_test.json')
preview_json = os.path.join(save_dir, 'preview.json')
preview_json_url = preview_json.replace('$$was_doc_root_path$$', '$$host_url$$')
cd_to_label_json = os.path.join(save_dir, 'code_to_label.json')
cd_to_label_json_url = cd_to_label_json.replace('$$was_doc_root_path$$', '$$host_url$$')

# 경로값 확인
print(f"mdl_nm == {mdl_nm}")
print(f"{os.path.exists(pwd)} / pwd == {pwd}")
print(f"{os.path.exists(raw_dat_dir)} / raw_dat_dir == {raw_dat_dir}")
print(f"{os.path.exists(save_dir)} / save_dir == {save_dir}")
print(f"{os.path.exists(prepared_db_dir)} / prepared_db_dir == {prepared_db_dir}")
print(f"{os.path.exists(step1_args_path)} / step1_args_path == {step1_args_path}")
print(f"{os.path.exists(summary_path)} / summary_path == {summary_path}")
print(f"{os.path.exists(pkl_path)} / pkl_path == {pkl_path}")

# Config File Writing
config['common_DL'] = { 'benchmark_dataset' : mdl_nm}

# Config File Save : Save Step1 argments
os.makedirs(summary_path, exist_ok=True)
with open(step1_args_path, 'w') as f:
    config.write(f)
print("Step1 args are saved")

print("Prepare {} dataset".format(mdl_nm))
if os.path.isfile(pkl_path):
    print("Load dataset")
    with open(pkl_path, 'rb') as f:
        database = pickle.load(f)
else:
    # Create Database Object
    # DataType : tf.data.Dataset

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
    elif mdl_nm == "mini_imagenet": # Tested. OK
        database=MiniImagenetDatabase(
            # 200831 changed path, add raw_data folder
            raw_data_address=raw_dat_dir,
            database_address=prepared_db_dir,
            random_seed=-1)
        print('database loaded')

    # Save the database file
    print(f"database={database}")
    print(f"pkl_path={pkl_path}")
    with open(pkl_path, 'wb') as f:
        pickle.dump(database, f) # e.g. for omniglot, ./dataset/data/ui_output/maml/step1/omniglot/omniglot.pkl
    # -> To load this file in the next step

# This code saves the stat of the dataset and the file path of each class
database.is_preview = True
database.get_statistic(base_path=raw_dat_dir, save_dir=summary_path)


# html 파일에서 사용하는 포맷으로 json 파일 작성
print(test_sample_json)
with open(test_sample_json, 'r') as json_file:
    test_sample_dict: dict = json.load(json_file)
preview_dict = {
    "images": []
}
for classnm, paths in test_sample_dict.items():
    for path in sorted(paths):
        preview_dict["images"].append({
            "label": classnm,
            "name": os.path.basename(path),
            "path": path.replace('$$was_doc_root_path$$', '$$host_url$$')
        })
classnms: list = sorted(test_sample_dict.keys())
cd_to_label_dict = dict(zip(range(len(classnms)), classnms))


with open(preview_json, 'w') as iowrapper:
    json.dump(preview_dict, iowrapper, indent='\t')
with open(cd_to_label_json, 'w') as iowrapper:
    json.dump(cd_to_label_dict, iowrapper, indent='\t')

print(preview_json_url)
print(cd_to_label_json_url)
