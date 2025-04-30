import os
import numpy as np
import csv
import json


# 결과json 파일을 읽어서 gt 랑 구간 비교하면서 얼마나 맞는지..
# 1. top-20 이 결과에 있는지 cnt해서 내기
# 2. 새로운 csv 만들어서 옆에 맞으면 몇 순위로 맞는지 rank 적기

GT_csv_path = "/Users/zzenninkim/dataset/sign_stream/ALL_data/2-Ben-Voice-Identity/2-Voice-Identity-GT.csv"
result_json = "/Users/zzenninkim/dataset/sign_stream/ALL_data/2-Ben-Voice-Identity/GT_segments_2-Ben-Voice-Identity__training_from_aslcitizen_0331004340_0.550341.pt.json"
output_csv_path = "/Users/zzenninkim/dataset/sign_stream/ALL_data/2-Ben-Voice-Identity/2-Voice-Identity-GT_arranged_training_from_aslcitizen_0331004340_0.550341.csv"



# --- 1. JSON 파일 먼저 읽어서 딕셔너리로 구성 ---
with open(result_json, 'r') as j_file:
    prediction_segments = json.load(j_file)

# (start_time, end_time) => top_predictions 로 빠르게 접근할 수 있는 딕셔너리 생성
segment_dict = {
    (round(float(seg[0]), 3), round(float(seg[1]), 3)): seg[2] for seg in prediction_segments
}

# --- 2. GT CSV 읽고, 딕셔너리에서 빠르게 탐색 ---
with open(GT_csv_path, 'r') as file, open(output_csv_path, 'w', newline='') as outfile:
    reader = csv.reader(file)
    writer = csv.writer(outfile)

    writer.writerow(["Video Name", "Start time", "End time", "Gloss", "Matched", "Rank", "Segment Start", "Segment End"])
    next(reader)  # skip header

    for row in reader:
        video_name = row[0]
        start_time = round(float(row[1]), 3)
        end_time = round(float(row[2]), 3)
        gt_gloss = row[3].strip().upper()

        matched = False
        rank = -1
        seg_start = None
        seg_end = None

        key = (start_time, end_time)

        if key in segment_dict:
            top_predictions = segment_dict[key]
            for idx, (pred_gloss, score) in enumerate(top_predictions):
                if pred_gloss.strip().upper() == gt_gloss:
                    matched = True
                    rank = idx + 1
                    seg_start = start_time
                    seg_end = end_time
                    break

        writer.writerow([video_name, start_time, end_time, gt_gloss, matched, rank, seg_start, seg_end])

print(f"완료! 결과 저장됨: {output_csv_path}")