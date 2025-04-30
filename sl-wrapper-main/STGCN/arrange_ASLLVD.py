import pandas as pd
import os
import numpy as np
import random
import re
import shutil
import json
# File paths
#video_info_file = "/Users/zzenninkim/dataset/ASLLVD/asllvd_signs_2024_06_27.csv"
#gloss_file = "/Users/zzenninkim/dataset/ASLLVD/Gloss_500_for_supplement.csv"

# Load the dataset
#video_df = pd.read_csv(video_info_file)
#gloss_df = pd.read_csv(gloss_file)

#make arranged csv file
#gloss_list = set(gloss_df["gloss"])
#filtered_df = video_df[video_df["Class Label"].isin(gloss_list)]
#output_csv = "./All_500_supplement_info.csv"
#filtered_df.to_csv(output_csv, index=False)

video_path = "/Users/zzenninkim/dataset/ASLLVD/videos_w/"
target_path = "/Users/zzenninkim/dataset/ASLLVD/videos_500/"
file = "./All_500_supplement_info.csv"

#input_file = "/Users/zzenninkim/dataset/ASLLVD/asllvd_signs_2024_06_27.csv"
#input_file = "/Users/zzenninkim/dataset/ASLLVD/asllvd_signs_cleaned_label_with_all_info.csv"
#input_file = "/Users/zzenninkim/dataset/ASLLVD/asllvd_signs_cleaned_label_996_glosses.csv"
gloss_file = "/Users/zzenninkim/dataset/ASLLRP/asllrp_991_gloss.csv"
#input_file = "/Users/zzenninkim/dataset/WLASL/WLASL_994.csv"
#input_file = "/Users/zzenninkim/dataset/WLASL/WLASL_994.csv"


input_file = "/Users/zzenninkim/dataset/WLASL/WLASL_991_labels.csv"
json_file = "/Users/zzenninkim/dataset/WLASL/start_kit/WLASL_v0.3.json"



# 1. 메타 데이터 불러오기
df = pd.read_csv(input_file)  # 메타 정보 파일
video_id_list = df["video_id"].astype(str).tolist()
# 2. JSON 불러오기
with open(json_file, "r") as f:
    json_data = json.load(f)

# 3. video_id 기준 필터링
filtered_data = []

for entry in json_data:
    new_instances = [
        inst for inst in entry["instances"] if str(inst["video_id"]) in video_id_list
    ]
    if new_instances:
        filtered_data.append({
            "gloss": entry["gloss"],
            "instances": new_instances
        })

# 4. 저장
with open("/Users/zzenninkim/dataset/WLASL/start_kit/WLASL_991_filtered.json", "w") as f:
    json.dump(filtered_data, f, indent=4)


# 2. gloss 리스트 불러오기
# gloss_list_df = pd.read_csv(gloss_file)  # 'Gloss' 열이 있는 파일
# gloss_list = gloss_list_df['Gloss'].astype(str).str.upper().str.strip().tolist()  # 대문자로 통일해서 비교
#
# # 3. 필터링
# filtered_df = df[df['cleaned_gloss'].isin(gloss_list)]
#
# # 4. 저장
# filtered_df.to_csv(output_file, index=False)

#
# def clean_label(label):
#     if pd.isna(label):  # 값이 NaN이면 빈 문자열 반환
#         return ""
#
#     # 모든 괄호 안의 문자 제거 (ex: "(1h)", "(25)", "(k)" 등)
#     label = re.sub(r"\(.*?\)", "", label)
#
#     # 숫자, 특수기호 제거 (`\`, `"`, `:`, `+`, `#` 등)
#     label = re.sub(r"\\|\"|:|\+|\#", "", label)
#
#     # 하이픈(-)과 언더스코어(_) 제거**
#     label = re.sub(r"[-_]", "", label)
#
#     # 단어 간 공백 제거 (연속된 공백도 없앰)
#     label = re.sub(r"\s+", "", label)
#     return label.strip()







# # 필요한 컬럼 이름을 가독성 있게 바꾸기 (선택사항)
# df = df.rename(columns={
#     "full video file": "video_file",
#     "start frame of the sign (relative to full videos)": "start_frame",
#     "end frame of the sign (relative to full videos)": "end_frame"
# })
#
# # 새로운 열 만들기: 파일 이름 형식
# df["generated_file_name"] = df.apply(
#     lambda row: f"{row['video_file'].replace('.mov', '')}_{int(row['start_frame'])}_{int(row['end_frame'])}.mov",
#     axis=1
# )
#
# # 결과 저장
# df.to_csv(output_file, index=False)
#
# print("✅ 새로운 파일 이름 열 추가 완료! 저장됨: final_with_generated_filename.csv")



# # gloss 리스트 불러오기
# gloss_df = pd.read_csv(gloss_file)
# gloss_list = gloss_df["Gloss"].str.upper().str.strip().tolist()
#
# # 전체 데이터 불러오기
# df = pd.read_csv(input_file)
#
# # Cleaned Label도 비교를 위해 대문자+공백제거 처리
# df["Cleaned Label"] = df["Cleaned Label"].str.upper().str.strip()
#
# # 필터링
# filtered_df = df[df["Cleaned Label"].isin(gloss_list)]
#
# # 결과 저장
# filtered_df.to_csv(output_file, index=False)
#
# print(f"✅ 완료! {len(filtered_df)}개의 행이 필터링되어 저장되었습니다: {output_file}")
#

#
#
# # 📌 해당하는 비디오 파일을 확인하고 이동
# for video in file_names:
#     video_file = row["full video file"]  # full video file 이름 가져오기
#     video_path = os.path.join(video_path, video_file)  # 원본 파일 경로 생성
#     destination_path = os.path.join(destination_dir, video_file)  # 이동할 경로 생성
#
#     # ✅ 파일 존재 여부 확인
#     if os.path.exists(video_path):
#         print(f"파일 이동 중: {video_file} → {destination_path}")
#         shutil.move(video_path, destination_path)  # 파일 이동
#
# file_names = df["full video file"].tolist()
#
# # 실제 디렉터리 내 파일 목록 가져오기
# files = set(os.listdir(video_path))  # set을 사용하면 검색 속도 향상
#
# # 존재하는 파일만 필터링
# existing_files = [file for file in file_names if file in files]
# existing_files = list(set(file_names) & files)
#
#
# # 존재하는 파일을 새로운 폴더로 이동
# for file in existing_files:
#     src = os.path.join(video_path, file)
#     dst = os.path.join(target_path, file)
#
#     try:
#         shutil.move(src, dst)
#         print(f"✅ Moved: {file}")
#     except Exception as e:
#         print(f"❌ Failed to move {file}: {e}")