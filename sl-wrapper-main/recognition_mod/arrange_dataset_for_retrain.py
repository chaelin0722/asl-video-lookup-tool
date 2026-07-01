import os
import json
import csv
import pandas as pd
import numpy as np
import re

# def clean_text(line):
#     # 숫자와 괄호 제거
#     line = re.sub(r"\(\d+h?\)", "", line)  # (1h), (25) 같은 표현 제거
#     #line = re.sub(r"\d+", "", line)  # 단독 숫자 제거
#
#     # 특수 문자 제거 (백슬래시, 따옴표, `+`, `:` 등)
#     line = re.sub(r"\\|\"|:|\+|\#", "", line)
#
#     # 단어 간 공백 제거
#     line = re.sub(r"\s+", "", line)
#
#     return line.strip()
#
#
# import pandas as pd
# import re
#
# # CSV files
# file_path1 = "/Users/zzenninkim/dataset/ASLLRP/asllrp_sentence_signs_2024_06_27.csv"
# file_path2 = "/Users/zzenninkim/dataset/ASLLRP/cleaned_gloss_labels.csv"
# df = pd.read_csv(file_path1, sep=",")   # 탭으로 구분된 파일이므로 delimiter 설정

#print(df.columns)
#Main entry gloss label 컬럼에서 정리된 텍스트 추출하는 함수
# def clean_label(label):
#     if pd.isna(label):  # 값이 NaN이면 빈 문자열 반환
#         return ""
#
#     # 1️⃣ 모든 괄호 안의 문자 제거 (ex: "(1h)", "(25)", "(k)" 등)
#     label = re.sub(r"\(.*?\)", "", label)
#
#     # 2️⃣ 숫자, 특수기호 제거 (`\`, `"`, `:`, `+`, `#` 등)
#     label = re.sub(r"\\|\"|:|\+|\#", "", label)
#
#     # 3️⃣ **하이픈(-)과 언더스코어(_) 제거** (이제 확실히 동작할 거예요!)
#     label = re.sub(r"[-_]", "", label)
#
#     # 4️⃣ 단어 간 공백 제거 (연속된 공백도 없앰)
#     label = re.sub(r"\s+", "", label)
#     return label.strip()
#
# # "Main entry gloss label" 컬럼 정리
# df["Cleaned Gloss Label"] = df["Main entry gloss label"].apply(clean_label)
#
# # 결과 출력
# print(df[["Main entry gloss label", "Cleaned Gloss Label"]])
#
# # 정리된 데이터를 CSV로 저장 (필요한 경우)
# df.to_csv("/Users/zzenninkim/dataset/ASLLRP/cleaned_gloss_labels.csv", index=False)
#
# #######
# df = pd.read_csv(file_path2, sep=",")
# # 중복 없이 유니크한 gloss 값만 추출
# unique_glosses = df["Cleaned Gloss Label"].dropna().unique()
#
# # 정렬해서 보기 쉽게 저장 (선택 사항)
# unique_glosses = sorted(unique_glosses)
#
# # 결과 출력
# print(f"Total unique glosses: {len(unique_glosses)}")
# print(unique_glosses[:20])  # 처음 20개만 확인 (필요 시 삭제)
#
# # 새로운 CSV 파일로 저장
# output_file_path = "/Users/zzenninkim/dataset/ASLLRP/asllrp_1913_glosses.csv"
# pd.DataFrame(unique_glosses, columns=["Unique Gloss"]).to_csv(output_file_path, index=False)
#
# print(f"Unique glosses saved to {output_file_path}")


asllrp = "/Users/zzenninkim/dataset/ASLLRP/asllrp_1913_glosses.csv"
asl2731 = "/Users/zzenninkim/dataset/ASLLRP/ASLcitizen_gloss_labels.csv"
output_path = "/Users/zzenninkim/dataset/ASLLRP/unique_glosses_marked.csv"

asllrp_df = pd.read_csv(asllrp)
asl2731_df = pd.read_csv(asl2731)

# Ensure columns are correctly named
asllrp_column = "Unique Gloss"  # Adjust if the column name is different
asl2731_column = "Sorted Gloss Labels"  # Adjust if the column name is different

# Convert ASLcitizen glosses to a set for fast lookup
asl2731_glosses = set(asl2731_df[asl2731_column].astype(str).str.strip())

# Add a new column 'ASLcitizen_Match' (1 if found in ASLcitizen, else 0)
asllrp_df["ASLcitizen_Match"] = asllrp_df[asllrp_column].astype(str).str.strip().apply(lambda x: 1 if x in asl2731_glosses else 0)

# Save the updated dataframe
asllrp_df.to_csv(output_path, index=False)

print(f"Processed file saved as: {output_path}")
