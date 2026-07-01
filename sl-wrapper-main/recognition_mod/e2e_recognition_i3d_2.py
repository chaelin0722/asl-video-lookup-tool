import sys
import os
from turtledemo.penrose import start
import copy
import torch
import pandas as pd
import numpy as np
import time
import argparse
import ffmpeg
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
model.load_state_dict(torch.load('./ASL_citizen_I3D_weights.pt',map_location=torch.device('cpu')))


model.train(False)

device = torch.device("cpu")
if torch.cuda.is_available():
    device = torch.device("cuda")

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



def load_rgb_frames_from_video(video_path, start_t, end_t, max_frames=64):
    """논문에서 사용된 ASLCitizen의 load_rgb_frames_from_video 함수"""

    vidcap = cv2.VideoCapture(video_path)
    #fps = vidcap.get(cv2.CAP_PROP_FPS)
    probe = ffmpeg.probe(video_path)
    fps = eval(probe['streams'][0]['r_frame_rate'])
    print("recognition ffmpeg fps: ", fps)
    # set start and end frame
    start_frame = round(start_t * fps)
    end_frame = round(end_t * fps)

    frames = []
    #total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    total_frames = end_frame - start_frame + 1

    frameskip = 1
    if total_frames >= 96:
        frameskip = 2
    if total_frames >= 160:
        frameskip = 3

    start = max(0, (total_frames - (max_frames * frameskip)) // 2)
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

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
    """논문 방식의 프레임 패딩"""
    if imgs.shape[0] < total_frames:
        pad_size = total_frames - imgs.shape[0]
        pad_frames = np.tile(imgs[0], (pad_size, 1, 1, 1))  # 첫 번째 프레임 복사
        imgs = np.concatenate([imgs, pad_frames], axis=0)
    return imgs


# 각 구간에 대해 비디오를 처리하고 인식 수행하는 함수
def recognize_segments_in_video(video_path, segment):
    result_list = []
    for start_t, end_t in segment:
        frames = load_rgb_frames_from_video(video_path, start_t, end_t)
        frames = pad_video_frames(frames)

        frames = frames.transpose(3, 0, 1, 2)  # (T, H, W, C) -> (C, T, H, W)
        inputs = torch.tensor(frames, dtype=torch.float32).unsqueeze(0).to(device)  # (1, C, T, H, W)
        # inputs shape (Batch, Channels, Frames, H, W)
        with torch.no_grad():
            per_frame_logits = model(inputs, pretrained=False)
            t = inputs.size(2)  # 원래 입력된 프레임 개수
            per_frame_logits = F.interpolate(per_frame_logits,
                                     size=(inputs.size(2), 2, 2),  # T, H, W 크기 지정
                                     mode='trilinear',
                                     align_corners=True)
            predictions = torch.max(per_frame_logits, dim=2)[0]
            pred = predictions.max(dim=-1).values.max(dim=-1).values # select highest value shape (1, 2731, 2, 2) -> (1, 2731)
            y_pred_tag = torch.softmax(pred, dim=1)
            pred_args = torch.argsort(y_pred_tag, dim=1, descending=True)


        # 상위 7개 결과 가져오기
        top_7_preds = pred_args[0][:7].tolist()
        top_7_confidences = y_pred_tag[0][pred_args[0][:7]].tolist()

        # Gloss mapping
        # 아래 두줄 확인하기
        df = pd.read_csv('output_gloss.csv')
        index_to_gloss = dict(zip(df["Index"], df["Gloss"]))
        mapped_labels = [index_to_gloss[idx] for idx in top_7_preds]
        gloss_pred = [[word, score] for word, score in zip(mapped_labels, top_7_confidences)]
        print("top 7 results: ", top_7_preds, ",", mapped_labels)
        result_list.append((start_t, end_t, gloss_pred))

    return result_list



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
    # BLEED
    # whole 3sec video -> video-1738166884037-814164221  (bleed 0.5 conf)
    # segmented 3sec video -> video-1738167416805-112955033 (x conf drops)
    # /Users/zzenninkim/dataset/ASL_Citizen
    #video_path = "/Users/zzenninkim/Documents/Research/sl-wrapper-main/60085579467325-APPLE.mp4"
    #segment_txt = "/Users/zzenninkim/Documents/Research/sl-wrapper-main/60085579467325-APPLE.txt"
    #video_path = "/Users/zzenninkim/Documents/Research/asl-search-automation-main/src/tmp/video-1738703027185-948488080.mp4"
    #segment_txt = "/Users/zzenninkim/Documents/Research/asl-search-automation-main/src/tmp/video-1738703027185-948488080.txt"
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

    print(f"Results saved to {output_json_path}")

