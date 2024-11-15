import sys
import os
from turtledemo.penrose import start
import copy
import torch
import pandas as pd
import numpy as np
import time
import argparse
from pympi.Elan import Eaf
import cv2
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from recognition_mod.spoter_mod.skeleton_extractor import obtain_pose_data, obtain_pose_data_frame
from recognition_mod.spoter_mod.normalization.body_normalization import \
    normalize_single_dict as normalize_single_body_dict, BODY_IDENTIFIERS
from recognition_mod.spoter_mod.normalization.hand_normalization import \
    normalize_single_dict as normalize_single_hand_dict, HAND_IDENTIFIERS


# 필요한 초기 설정
HAND_IDENTIFIERS = [id + "_Left" for id in HAND_IDENTIFIERS] + [id + "_Right" for id in HAND_IDENTIFIERS]
GLOSS = ['bowling', 'africa', 'cheat', 'decide', 'letter', 'laugh', 'blanket', 'cute', 'leave', 'lose', 'problem',
         'share', 'approve', 'convince', 'country', 'crash', 'government', 'hope', 'order', 'president', 'russia',
         'since', 'theory', 'war', 'champion', 'delay', 'delicious', 'disappear', 'fault', 'humble', 'kill', 'law',
         'kiss', 'wrong', 'none', 'thin', 'school', 'beard', 'glasses', 'cow', 'make', 'cry', 'fine', 'ball', 'write',
         'learn', 'orange', 'thursday', 'walk', 'family', 'why', 'book', 'ride', 'cereal', 'football', 'who', 'ugly',
         'yesterday', 'cousin', 'cook', 'friendly', 'want', 'dance', 'train', 'go', 'business', 'christmas', 'old',
         'coffee', 'apple', 'play', 'computer', 'crazy', 'hard', 'work', 'girl', 'salt', 'read', 'yellow', 'cat',
         'match', 'internet', 'drink', 'but', 'sick', 'headache', 'boy', 'color', 'paper', 'what', 'close', 'stay',
         'tall', 'water', 'eat', 'bad', 'good', 'more', 'milk', 'know']

df = pd.read_csv("/Users/zzenninkim/Documents/Research/sl-wrapper-main/recognition_mod/final-gloss-specifier.csv", encoding="utf-8")
df = df.fillna("—")

model = torch.load("/Users/zzenninkim/Documents/Research/sl-wrapper-main/recognition_mod/spoter-checkpoint.pth", map_location=torch.device('cpu'))
model.train(False)

device = torch.device("cpu")
if torch.cuda.is_available():
    device = torch.device("cuda")

def tensor_to_dictionary(landmarks_tensor: torch.Tensor) -> dict:

    data_array = landmarks_tensor.numpy()
    output = {}


    for landmark_index, identifier in enumerate(BODY_IDENTIFIERS + HAND_IDENTIFIERS):
        output[identifier] = data_array[:, landmark_index]

    return output


def dictionary_to_tensor(landmarks_dict: dict) -> torch.Tensor:

    output = np.empty(shape=(len(landmarks_dict["leftEar"]), len(BODY_IDENTIFIERS + HAND_IDENTIFIERS), 2))

    for landmark_index, identifier in enumerate(BODY_IDENTIFIERS + HAND_IDENTIFIERS):
        output[:, landmark_index, 0] = [frame[0] for frame in landmarks_dict[identifier]]
        output[:, landmark_index, 1] = [frame[1] for frame in landmarks_dict[identifier]]

    return torch.from_numpy(output)



# 시간 구간을 읽어오는 함수
def read_time_segments(file_path):
    segments = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(', ')
            start_time = float(parts[0].replace('Start: ', '').replace(' sec', ''))
            end_time = float(parts[1].replace('End: ', '').replace(' sec', ''))
            segments.append((start_time, end_time))
    return segments


# 각 구간에 대해 비디오를 처리하고 인식 수행하는 함수
def recognize_segments_in_video(video_path, segments):
    results = []

    # 비디오 객체 생성
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    for start_time, end_time in segments:
        # 시작 프레임과 끝 프레임 계산
        start_frame = round(start_time * fps)
        end_frame = round(end_time * fps)

        # 필요한 구간만큼 비디오 읽기
        data, frames = obtain_pose_data_frame(video_path, start_frame, end_frame)

        # landmark 갯수  /   body identifier -> 12개 , hand identifier -> 42    /    2 -> x,y
        depth_map = np.empty(shape=(len(data.data_hub["nose_X"]), len(BODY_IDENTIFIERS + HAND_IDENTIFIERS), 2))

        # depth_map 에다가 각 keypoint 54개의 x,y 정보를 옮겨 닮는다.
        for index, identifier in enumerate(BODY_IDENTIFIERS + HAND_IDENTIFIERS):
            depth_map[:, index, 0] = data.data_hub[identifier + "_X"]
            depth_map[:, index, 1] = data.data_hub[identifier + "_Y"]

        depth_map = torch.from_numpy(np.copy(depth_map))

        depth_map = tensor_to_dictionary(depth_map)
        # 예시, depth_map["nose"][0] 하면, 0번째 프레임의 Nose 에 대한 x,y 좌표가 나온다.

        keys = copy.copy(list(depth_map.keys()))
        for key in keys:
            data = depth_map[key]
            del depth_map[key]
            depth_map[key.replace("_Left", "_0").replace("_Right", "_1")] = data

        depth_map = normalize_single_body_dict(depth_map)
        depth_map = normalize_single_hand_dict(depth_map)

        keys = copy.copy(list(depth_map.keys()))
        for key in keys:
            data = depth_map[key]
            del depth_map[key]
            depth_map[key.replace("_0", "_Left").replace("_1", "_Right")] = data

        depth_map = dictionary_to_tensor(depth_map)

        depth_map = depth_map - 0.5

        # 모델에 입력하고 결과 저장
        inputs = depth_map.squeeze(0).to(device)

        # check each segments' input shape
        #print(f"Inputs shape: {inputs.shape} for segment {start_time}-{end_time}")

        if len(inputs.shape) != 3:
            print(f"Skipping segment {start_time}-{end_time} due to incorrect input shape: {inputs.shape}")
            continue

        outputs = model(inputs).expand(1, -1, -1)
        probabilities = torch.nn.functional.softmax(outputs, dim=2).detach().cpu().numpy()[0, 0]

        # 각 구간에 대한 결과를 저장
        gloss_results = {GLOSS[i]: float(probabilities[i]) for i in range(100)}
        top_results = sorted(gloss_results.items(), key=lambda x: x[1], reverse=True)[:7]  # 상위 7개 결과
        results.append((start_time, end_time, top_results))

    cap.release()
    return results


# pose 데이터 전처리
def preprocess_pose_data(pose_data):
    depth_map = np.empty(shape=(len(pose_data["nose_X"]), len(BODY_IDENTIFIERS + HAND_IDENTIFIERS), 2))

    # depth_map 에다가 각 keypoint 54개의 x,y 정보를 옮겨 닮는다.
    for index, identifier in enumerate(BODY_IDENTIFIERS + HAND_IDENTIFIERS):
        depth_map[:, index, 0] = pose_data[identifier + "_X"]
        depth_map[:, index, 1] = pose_data[identifier + "_Y"]

    depth_map = torch.from_numpy(np.copy(depth_map))
    depth_map = tensor_to_dictionary(depth_map)

    # 전처리 과정: normalize -> tensor 변환 -> 모델 입력값 조정
    depth_map = normalize_single_body_dict(depth_map)
    depth_map = normalize_single_hand_dict(depth_map)
    depth_map = dictionary_to_tensor(depth_map)
    depth_map = depth_map - 0.5

    return depth_map


# dictionary와 tensor 간 변환 함수들
def tensor_to_dictionary(landmarks_tensor: torch.Tensor) -> dict:
    data_array = landmarks_tensor.numpy()
    output = {}
    for landmark_index, identifier in enumerate(BODY_IDENTIFIERS + HAND_IDENTIFIERS):
        output[identifier] = data_array[:, landmark_index]
    return output


def dictionary_to_tensor(landmarks_dict: dict) -> torch.Tensor:
    output = np.empty(shape=(len(landmarks_dict["leftEar"]), len(BODY_IDENTIFIERS + HAND_IDENTIFIERS), 2))
    for landmark_index, identifier in enumerate(BODY_IDENTIFIERS + HAND_IDENTIFIERS):
        output[:, landmark_index, 0] = [frame[0] for frame in landmarks_dict[identifier]]
        output[:, landmark_index, 1] = [frame[1] for frame in landmarks_dict[identifier]]
    return torch.from_numpy(output)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_segtxt', required=True, type=str, help='path to input segment txt file')
    parser.add_argument('--video', default=None, required=False, type=str, help='path to video file')

    return parser.parse_args()
# 실행 부분
if __name__ == "__main__":
    args = get_args()
    video_path = args.video
    segment_txt = args.input_segtxt

    print("Start ASL recognition")

    #video_path = "/Users/zzenninkim/Documents/Research/sl-wrapper-main/60085579467325-APPLE.mp4"
    #segment_txt = "/Users/zzenninkim/Documents/Research/sl-wrapper-main/60085579467325-APPLE.txt"
    #output_json_path = "/Users/zzenninkim/Documents/Research/sl-wrapper-main/results"

    # 구간마다의 정보 가져오기
    segments = read_time_segments(segment_txt)

    # 각 구간에 대해 sign recognition 수행
    start_time = time.time()
    recognition_results = recognize_segments_in_video(video_path, segments)
    end_time = time.time()

    # 처리 시간 계산 및 기록
    processing_time = end_time - start_time

    print(f"Processing time for {segment_txt}: {processing_time:.2f} seconds")

    # JSON 파일로 결과 저장
    output_json_path = os.path.join(segment_txt.split(".")[0] + ".json")
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(recognition_results, json_file, ensure_ascii=False, indent=4)


    # 결과 출력
    for start_time, end_time, predictions in recognition_results:
        print(f"Segment from {start_time} to {end_time}:")
        for gloss, confidence in predictions:
            print(f"    Gloss: {gloss}, Confidence: {confidence:.2f}")


