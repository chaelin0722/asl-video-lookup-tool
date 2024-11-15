import os
import sys
from turtledemo.penrose import start

from setuptools.dist import sequence

from recognition_mod import spoter
import copy
import torch
import pandas as pd
import numpy as np
from pympi.Elan import Eaf

import cv2
from recognition_mod.spoter_mod.skeleton_extractor import obtain_pose_data, obtain_pose_data_with_frames
from recognition_mod.spoter_mod.normalization.body_normalization import normalize_single_dict as normalize_single_body_dict, BODY_IDENTIFIERS
from recognition_mod.spoter_mod.normalization.hand_normalization import normalize_single_dict as normalize_single_hand_dict, HAND_IDENTIFIERS

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

df = pd.read_csv("./final-gloss-specifier.csv", encoding="utf-8")
df = df.fillna("—")

model = torch.load("./spoter-checkpoint.pth", map_location=torch.device('cpu'))
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


def recognize_sign(video_path, n_include=10) -> (list, list):

    # 108 종류의 keypoint 들이 fps 만큼 저장되어있음 fps = 14.93
    #data = obtain_pose_data(video_path)
    data = obtain_pose_data_with_frames(video_path)

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

    ## 여기다가 fps 기준 각 구간만큼 Recognition 반복 수행! for ans

    #frame_index = round(len(sequence_list) * fps)

    inputs = depth_map.squeeze(0).to(device)
    outputs = model(inputs).expand(1, -1, -1)
    results = torch.nn.functional.softmax(outputs, dim=2).detach().numpy()[0, 0]

    results = {GLOSS[i]: float(results[i]) for i in range(100)}
    class_confs = []

    for pred_class in sorted(results, key=results.get, reverse=True)[:n_include]:
        if int(results[pred_class] * 100):
            class_confs.append(int(results[pred_class] * 100))
        else:
            class_confs.append(1)

    top_pred_class = sorted(results, key=results.get, reverse=True)[:n_include]
    top_pred_conf = class_confs[:n_include]

    return top_pred_class, top_pred_conf



if __name__ == "__main__":
    video_path = sys.argv[1] if len(sys.argv) > 1 else "/default/path/to/video.mp4"
    x, y = recognize_sign(video_path)
    print("??")
    print("class", x, "preds", y)


''' 
if __name__ == "__main__":

    x, y = recognize_sign("/Users/zzenninkim/Documents/Research/sl-wrapper-main/clips/clip_30s_preprocess.mp4")



    print(x,y)
'''