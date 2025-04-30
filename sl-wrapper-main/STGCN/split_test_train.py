import pandas as pd
import numpy as np
import random
###
"""
1. Shuffles each gloss group.
2. make sure train as at least one unique gloss (1913) 
2.	Selects 3-4 test samples for glosses that appear frequently.
3.	Maintains a 70-30 overall ratio 
"""
###

# File paths
input_file = "/Users/zzenninkim/dataset/ASLLRP/ASLLRP_ASLLVD_996_gloss_all_data.csv"
gloss_file = "/Users/zzenninkim/dataset/ASLLRP/asllrp_1000_gloss.csv"

'''
# Gloss 리스트 불러오기
gloss_df = pd.read_csv(gloss_file, header=None)  # Header가 없으면 header=None 지정
gloss_list = set(gloss_df[0].tolist())  # Set으로 변환하여 검색 속도 최적화

# 필터링할 데이터 불러오기
data_df = pd.read_csv(input_file)

# Cleaned Gloss Label이 Gloss 리스트에 있는 경우만 유지
filtered_df = data_df[data_df["Cleaned Gloss Label"].isin(gloss_list)]

# 결과 저장
filtered_df.to_csv(output_file, index=False)


'''


train_file = "/Users/zzenninkim/dataset/ASLLRP/asllrp_asllvd_train_996.csv"
test_file = "/Users/zzenninkim/dataset/ASLLRP/asllrp_asllvd_test_996.csv"
all_996_data_file = "/Users/zzenninkim/dataset/ASLLRP/ASLLRP_ASLLVD_996_gloss_all_data.csv"
# Load the dataset
df = pd.read_csv(all_996_data_file)

# 헤더를 제외한 데이터만 사용
df = df.iloc[1:]
# Dictionary to store train and test splits
train_data = []
test_data = []

# Group by gloss label
grouped = df.groupby("gloss")

# Train과 Test 데이터 저장할 리스트
train_data = []
test_data = []

# 모든 고유한 gloss 리스트
unique_glosses = df["gloss"].unique()




# 먼저 각 gloss에서 하나씩은 train에 추가
for gloss in unique_glosses:
    gloss_videos = grouped.get_group(gloss).values.tolist()
    selected = random.choice(gloss_videos)  # 하나 랜덤 선택
    train_data.append(selected)
    gloss_videos.remove(selected)  # 선택된 것은 제거

    # 남은 데이터에서 train/test 나누기
    random.shuffle(gloss_videos)
    split_idx = int(len(gloss_videos) * 0.6)

    train_data.extend(gloss_videos[:split_idx])
    test_data.extend(gloss_videos[split_idx:])

# DataFrame으로 변환
train_df = pd.DataFrame(train_data, columns=df.columns)
test_df = pd.DataFrame(test_data, columns=df.columns)

# CSV로 저장
train_df.to_csv(train_file, index=False)
test_df.to_csv(test_file, index=False)

print(f"Train set: {len(train_df)} samples")
print(f"Test set: {len(test_df)} samples")
print(f"Total unique glosses in Train: {len(train_df['gloss'].unique())}")
print(f"Total unique glosses in Test: {len(test_df['gloss'].unique())}")
