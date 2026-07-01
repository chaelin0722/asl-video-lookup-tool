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

from pytorch_i3d import InceptionI3d
import torch.nn.functional as F
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))


# sl-wrapper-main, conda activate sl-wrapper-py38
# model = torch.load("/Users/zzenninkim/Documents/Research/sl-wrapper-main/recognition_mod/spoter-checkpoint.pth", map_location=torch.device('cpu'))
# CHI-2025-SLD , conda activate SLD-2025

model = InceptionI3d(2731, in_channels=3)

#model.replace_logits(2731)
#print(model.logits.out_features)
#Update model weights here
model.load_state_dict(torch.load('/Users/zzenninkim/Documents/Research/CHI-2025-SLD/chi2025-sign-language-dictionary-main/gradio-recognition-screen/ASL_citizen_I3D_weights.pt',map_location=torch.device('cpu')))


model.train(False)

device = torch.device("cpu")
if torch.cuda.is_available():
    device = torch.device("cuda")


def load_rgb_frames_from_video(video_path, max_frames=64):
    """  load_rgb_frames_from_video  """
    vidcap = cv2.VideoCapture(video_path)
    frames = []
    total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))

    frameskip = 1
    if total_frames >= 96:
        frameskip = 2
    if total_frames >= 160:
        frameskip = 3

    start = max(0, (total_frames - (max_frames * frameskip)) // 2)
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, start)

    for _ in range(min(max_frames * frameskip, total_frames - start)):
        success, img = vidcap.read()
        if not success:
            break
        if len(frames) % frameskip == 0:
            img = cv2.resize(img, (256, 256))
            img = (img / 255.0) * 2 - 1
            frames.append(img)

    vidcap.release()
    return np.asarray(frames, dtype=np.float32)


def pad_video_frames(imgs, total_frames=64):
    """according to paper.."""
    if imgs.shape[0] < total_frames:
        pad_size = total_frames - imgs.shape[0]
        pad_frames = np.tile(imgs[0], (pad_size, 1, 1, 1))  # 첫 번째 프레임 복사
        imgs = np.concatenate([imgs, pad_frames], axis=0)
    return imgs


# read from segments
def read_time_segments(file_path):
    segments = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(', ')
            start_time = float(parts[0].replace('Start: ', '').replace(' sec', ''))
            end_time = float(parts[1].replace('End: ', '').replace(' sec', ''))
            segments.append((start_time, end_time))
    return segments


# run whole video
def recognize_segments_in_video(video_path):
    frames = load_rgb_frames_from_video(video_path)
    frames = pad_video_frames(frames)

    frames = frames.transpose(3, 0, 1, 2)  # (T, H, W, C) -> (C, T, H, W)
    inputs = torch.tensor(frames, dtype=torch.float32).unsqueeze(0).to(device)  # (1, C, T, H, W)
    # inputs shape (Batch, Channels, Frames, H, W)
    with torch.no_grad():
        per_frame_logits = model(inputs, pretrained=False)
        t = inputs.size(2)
        ###############################
        ### upsampling
        per_frame_logits = F.interpolate(per_frame_logits,
                                 size=(inputs.size(2), 2, 2),  # T, H, W
                                 mode='trilinear',
                                 align_corners=True)
        predictions = torch.max(per_frame_logits, dim=2)[0]
        pred = predictions.max(dim=-1).values.max(dim=-1).values # select highest value shape (1, 2731, 2, 2) -> (1, 2731)
        y_pred_tag = torch.softmax(pred, dim=1)
        pred_args = torch.argsort(y_pred_tag, dim=1, descending=True)


    # top 7 results
    top_7_preds = pred_args[0][:7].tolist()
    top_7_confidences = y_pred_tag[0][pred_args[0][:7]].tolist()

    # Gloss mapping
    df = pd.read_csv('output_gloss.csv')
    index_to_gloss = dict(zip(df["Index"], df["Gloss"]))
    mapped_labels = [index_to_gloss[idx] for idx in top_7_preds]

    print("top 7 results: ", top_7_preds, ",", mapped_labels)
    return list(zip(mapped_labels, top_7_confidences))




def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_segtxt', required=True, type=str, help='path to input segment txt file')
    parser.add_argument('--video', default=None, required=False, type=str, help='path to video file')

    return parser.parse_args()



if __name__ == "__main__":
    #args = get_args()
    #video_path = args.video
    #segment_txt = args.input_segtxt

    print("Start ASL recognition")
    '''
    train_csv_file = "/Users/zzenninkim/dataset/ASL_Citizen/splits/test.csv"
    dir = "/Users/zzenninkim/dataset/ASL_Citizen/videos"

    video_lists = [f for f in os.listdir(dir) if f.endswith(".mp4")]
    output_json_path = "/Users/zzenninkim/dataset/ASL_Citizen/output/test_4/"

    df = pd.read_csv(train_csv_file, delimiter=",", header=0)  # Ensure tab delimiter is handled
    valid_video_files = set(df["Video file"].tolist())  # Extract filenames


    for video_file in os.listdir(dir):
       if video_file in valid_video_files:  #
            video_path = os.path.join(dir, video_file)
            # 각 구간에 대해 sign recognition 수행
            # video path
            #video_path = "/Users/zzenninkim/dataset/ASL_Citizen/videos/708519754475585-PREFER.mp4"
            print("processing video: ", video_file)
            start_time = time.time()
            recognition_results = recognize_segments_in_video(video_path)
            end_time = time.time()

            # 처리 시간 계산 및 기록
            processing_time = end_time - start_time

            formatted_results = []
            for glosses, confidences in recognition_results:
                # glosses와 confidences를 쌍으로 묶어 리스트로 구성
                predictions = [[gloss, float(confidence)] for gloss, confidence in zip([glosses], [confidences])]
                formatted_results.append([predictions])

            # JSON 파일로 결과 저장
            output_dir = os.path.join(output_json_path + video_file + ".json") ####
            with open(output_dir, 'w', encoding='utf-8') as json_file:
                json.dump(formatted_results, json_file, ensure_ascii=False, indent=4)

            print(f"Results saved to {output_json_path}")

    '''
    ## check the performance!
    path_to_resultscsv = "/Users/zzenninkim/dataset/ASL_Citizen/output/test_4/"
    json_lists = [f for f in os.listdir(path_to_resultscsv) if f.endswith(".json")]

    train_csv_file = "/Users/zzenninkim/dataset/ASL_Citizen/splits/test.csv"
    df = pd.read_csv(train_csv_file, delimiter=",", header=0)  # Ensure tab delimiter is handled

    output_results_file = "/Users/zzenninkim/dataset/ASL_Citizen/output/test4_result.txt"
    count = 0
    rank_list = [0,0,0,0,0,0,0]
    for file in json_lists:
        file_name = file.split(".json")[0]
        ##
        matching_gloss = df.loc[df["Video file"] == file_name, "Gloss"].values
        with open(os.path.join(path_to_resultscsv, file), "r", encoding="utf-8") as file:
            json_data = json.load(file)

        for i in range(len(json_data)):
            gloss = json_data[i][0][0][0]
            conf = json_data[i][0][0][1]

            if matching_gloss == gloss:
                print(file_name, f" matched in {i}th rank,", gloss)
                rank_list[i] = rank_list[i] + 1
                #with open(output_results_file, 'a', encoding="utf-8") as ofile:
                #    ofile.write(f"Gloss: {gloss} found in {i}th rank\n")
                count += 1
                break

    print("# of found", count)
    print("rank list", rank_list)
