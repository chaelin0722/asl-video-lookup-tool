import math
import os
import subprocess
import argparse
import ffmpeg

#os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
#os.environ["CUDA_VISIBLE_DEVICES"] = '3'
import json
import torch
import torch.nn
import time
import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
from pathlib import Path

# Initialize mediapipe drawing class - to draw the landmarks points.
mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic


from architecture.st_gcn import STGCN
from architecture.fc import FC
from architecture.network import Network

#Given a sorted output from the model aka ranked list, returns
#rank of ground truth and list of other metrics
#The different indices correspond to [DCG, Top-1 Acc, Top-5 Acc, Top-10 Acc, Top-20 Acc, MRR]
def eval_metrics(sortedArgs, label):
    res, = np.where(sortedArgs == label)
    dcg = 1 / math.log2(res[0] + 1 + 1) #res values start from 0
    mrr = 1 / (res[0] + 1)
    if res < 1:
        return res[0], [dcg, 1, 1, 1, 1, mrr]
    elif res < 5:
        return res[0], [dcg, 0, 1, 1, 1, mrr]
    elif res < 10:
        return res[0], [dcg, 0, 0, 1, 1, mrr]
    elif res < 20:
        return res[0], [dcg, 0, 0, 0, 1, mrr]
    else:
        return res[0], [dcg, 0, 0, 0, 0, mrr]

torch.manual_seed(0)
np.random.seed(0)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
torch.set_default_dtype(torch.float64)


#Update files and paths as needed
video_base_path = '../data/poses/'
train_file = '../data_csv/aslcitizen_training_set.csv'
test_file = '../data_csv/aslcitzen_test_set.csv'
#Update names according to experiment number
tag = 'experiment1b'
dataset_name = "training_full"

device = torch.device("cpu")
'''
train_transforms = pose_transforms.Compose([pose_transforms.ShearTransform(0.1),
                                            pose_transforms.RotatationTransform(0.1)])
#load data
train_ds = Dataset(datadir=video_base_path, video_file=train_file, transforms=train_transforms, pose_map_file = "pose_mapping_train.csv")
test_ds = Dataset(datadir=video_base_path, video_file=test_file, gloss_dict=train_ds.gloss_dict, pose_map_file = "pose_mapping_test.csv")
n_classes = len(train_ds.gloss_dict)


test_loader = torch.utils.data.DataLoader(test_ds, batch_size=1, shuffle=True, num_workers=2, pin_memory=True)
'''



n_classes = 991
#load model
n_features = 256
graph_args = {'num_nodes': 27, 'center': 0,
              'inward_edges': [[2, 0], [1, 0], [0, 3], [0, 4], [3, 5],
                               [4, 6], [5, 7], [6, 17], [7, 8], [7, 9],
                               [9, 10], [7, 11], [11, 12], [7, 13], [13, 14],
                               [7, 15], [15, 16], [17, 18], [17, 19], [19, 20],
                               [17, 21], [21, 22], [17, 23], [23, 24], [17, 25], [25, 26]]}
stgcn = STGCN(in_channels=2, graph_args=graph_args, edge_importance_weighting=True)
fc = FC(n_features=n_features, num_class=n_classes, dropout_ratio=0.05)
pose_model = Network(encoder=stgcn, decoder=fc) 
weights_path = "/sl-wrapper-main/recognition_mod/STGCN/ALL_weights/_training_from_citizen_june02145024_0.690164.pt" 

#checkpoint = torch.load(weights_path, map_location="cpu")
#model_state_dict = checkpoint["model_state_dict"]
#pose_model.load_state_dict(model_state_dict)

# pose_model.load_state_dict(torch.load(weights_path,map_location=torch.device('cpu')))

#### original
# checkpoint = torch.load(weights_path, map_location=torch.device('cpu'))
# pose_model.load_state_dict(checkpoint["model_state_dict"])
# pose_model.to(device)
####

checkpoint = torch.load(weights_path, map_location=torch.device('cpu'))
pose_model.load_state_dict(checkpoint["model_state_dict"])
pose_model.to(device)


pose_model.train(False)  # Set model to evaluate mode


def extract_landmarks(video_path):
    f = video_path

    with mp_holistic.Holistic(
            static_image_mode=False, min_detection_confidence=0.5) as holistic:

        video = cv2.VideoCapture(f)
        total_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)

        feature = np.zeros((int(total_frames), 543, 2))
        count = 0
        success = 1

        while success:
            success, image = video.read()
            if success:
                results = holistic.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

                for i in range(33):
                    if results.pose_landmarks:
                        feature[count][i][0] = results.pose_landmarks.landmark[i].x
                        feature[count][i][1] = results.pose_landmarks.landmark[i].y

                j = 33
                for i in range(21):
                    if results.right_hand_landmarks:
                        feature[count][i + j][0] = results.right_hand_landmarks.landmark[i].x
                        feature[count][i + j][1] = results.right_hand_landmarks.landmark[i].y

                j = 54
                for i in range(21):
                    if results.left_hand_landmarks:
                        feature[count][i + j][0] = results.left_hand_landmarks.landmark[i].x
                        feature[count][i + j][1] = results.left_hand_landmarks.landmark[i].y

                j = 75
                for i in range(468):
                    if results.face_landmarks:
                        feature[count][i + j][0] = results.face_landmarks.landmark[i].x
                        feature[count][i + j][1] = results.face_landmarks.landmark[i].y
                count += 1

        np.save(os.path.splitext(video_path)[0] + '.npy', feature)
        return os.path.splitext(video_path)[0] + '.npy'



# read time
def read_time_segments(file_path):
    segments = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(', ')
            start_time = float(parts[0].replace('Start: ', '').replace(' sec', ''))
            end_time = float(parts[1].replace('End: ', '').replace(' sec', ''))
            segments.append((start_time, end_time))
    return segments

def downsample(frames, max_frames):
    length = frames.shape[0]
    # Adjust FPS dynamically based on length of video
    increment = max_frames / length  # determine increment based on number of frames
    if increment > 1.0:
        increment = 1.0  # if already less than max_frames, keep it
    curr_increment = 0
    curr_frame = 0
    new_frames = []
    for f in frames:
        curr_increment += increment
        if curr_increment > curr_frame:
            curr_frame += 1
            new_frames.append(f)
    if len(new_frames) > max_frames:
        new_frames = new_frames[:max_frames]  # cut off if 128 frames exceed
    return np.array(new_frames)


def recognize_segments_in_video(pose_npy_path, segment, fps):
    result_list = []
    # asl citizen
    #df = pd.read_csv('/Users/zzenninkim/Research/sl-wrapper-main/recognition_mod/output_gloss.csv')
    # asllrp
    df = pd.read_csv('/Users/zzenninkim/dataset/ASLLRP/asllrp_991_gloss.csv')
    index_to_gloss = dict(zip(df["Index"], df["Gloss"]))
    cnt = 0
    for start_t, end_t in segment:
        print(f"segment{cnt}, processing")
        start_frame = int(start_t * fps)
        end_frame = int(end_t * fps)
        print("start and end frame:", start_frame, end_frame)
        # .npy  (T, V, C) == (num of frames, num of landmarks, XY)
        pose_data = np.load(pose_npy_path)

        # (T, C, V) → (T', C, V)
        segmented_pose_data = pose_data[start_frame:end_frame+1, :, :]  # use only selected frames
        length = segmented_pose_data.shape[0]

        #segmented_pose_data = pose_data
        #length = segmented_pose_data.shape[0]

        if length > 128:
            segmented_pose_data = downsample(segmented_pose_data, 128)  # cut off if 128 frames exceed
        if length < 128:
            segmented_pose_data = np.pad(segmented_pose_data, ((0, 128 - length), (0, 0), (0, 0)))  # pad if less than 128 frames


        shoulder_l = segmented_pose_data[:, 11, :]
        shoulder_r = segmented_pose_data[:, 12, :]

        center = np.zeros(2)
        for i in range(len(shoulder_l)):
            center_i = (shoulder_r[i] + shoulder_l[i]) / 2
            center = center + center_i
        center = center / shoulder_l.shape[0]

        mean_dist = np.mean(np.sqrt(((shoulder_l - shoulder_r) ** 2).sum(-1)))
        if mean_dist != 0:
            scale = 1.0 / mean_dist
            segmented_pose_data  = segmented_pose_data  - center
            segmented_pose_data  = segmented_pose_data  * scale


        keypoints = [0, 2, 5, 11, 12, 13, 14, 33, 37, 38, 41, 42, 45, 46,
                    49, 50, 53, 54, 58, 59, 62, 63, 66, 67, 70, 71, 74]

        segmented_pose_data = segmented_pose_data[:, 0:75, :]
        posedata = segmented_pose_data[:, 0:33, :]  #
        lhdata = segmented_pose_data[:, 54:, :]  #
        rhdata = segmented_pose_data[:, 33:54, :]  #

        data = np.concatenate([posedata, lhdata, rhdata], axis=1)
        data = data[:, keypoints, :]
        data = np.transpose(data, (2, 0, 1))  # (T, V, C) → (C, T, V)  xy, frames, num of landmarks
        #segmented_pose_data = segmented_pose_data[:, :, keypoints_idx]  # (C, T, V) → (C, T, 27)


        # change to tensor
        inputs = torch.from_numpy(data).double()
        inputs = inputs.unsqueeze(0)  # (C, T, V) → (1, C, T, V)

        # inputs.shape == (N, C, T, V)  # (batch, channels, frames, keypoints)
        predictions = pose_model(inputs)

        y_pred_tag = torch.softmax(predictions, dim=1)
        # check = torch.argsort(predictions, dim=1, descending=True)
        pred_args = torch.argsort(y_pred_tag, dim=1, descending=True)

        # bring top 20 results
        top_20_preds = pred_args[0][:20].tolist()
        top_20_confidences = y_pred_tag[0][pred_args[0][:20]].tolist()

        # Gloss mapping
        mapped_labels = [index_to_gloss[idx] for idx in top_20_preds]
        gloss_pred = [[word, score] for word, score in zip(mapped_labels, top_20_confidences)]
        #print("top 20 results: ", top_20_preds, ",", mapped_labels)
        result_list.append((start_t, end_t, gloss_pred)) # original
        #result_list.append(gloss_pred)
        cnt += 1


    return result_list


def convert_to_mp4(video_path):
    """
    Convert WebM file to MP4 using FFmpeg.
    """
    output_mp4 = os.path.splitext(video_path)[0] + ".mp4"

    # if WebM file, convert to mp4
    if not video_path.lower().endswith(".mp4"):
        print(f"Converting {video_path} to {output_mp4}...")
        command = [
            "ffmpeg", "-i", video_path, "-c:v", "libx264", "-preset", "fast",
            "-crf", "23", "-c:a", "aac", "-b:a", "128k", output_mp4, "-y"
        ]
        subprocess.run(command, check=True)
        print(f"Conversion complete: {output_mp4}")
        return output_mp4

    return video_path  # return if it is mp4


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_segtxt', required=True, type=str, help='path to input segment txt file')
    parser.add_argument('--video', default=None, required=False, type=str, help='path to video file')

    return parser.parse_args()

# main
if __name__ == "__main__":
    args = get_args()
    video_path = args.video
    segment_txt = args.input_segtxt
 
    overlap_file = video_path.split(".mp4")[0] + ".json"

    if os.path.exists(overlap_file):
        print(f"JSON file already exists: {overlap_file}")
        print("DONE")
        exit()
    ####

    video_path = convert_to_mp4(video_path)

    vidcap = cv2.VideoCapture(video_path)
    #fps = vidcap.get(cv2.CAP_PROP_FPS)
    probe = ffmpeg.probe(video_path)
    
    # Safe FPS extraction with fallback
    try:
        r_frame_rate = probe['streams'][0]['r_frame_rate']
        if '/' in r_frame_rate:
            numerator, denominator = r_frame_rate.split('/')
            if int(denominator) != 0:
                fps = int(numerator) / int(denominator)
            else:
                fps = 30.0  # fallback FPS
        else:
            fps = float(r_frame_rate)
    except (KeyError, ValueError, ZeroDivisionError):
        # Fallback to OpenCV if FFmpeg fails
        fps = vidcap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30.0  # default FPS if all else fails
    
    print("fps: ", fps)
    # bring info from segments
    segments = read_time_segments(segment_txt)

    pose_npy_path = extract_landmarks(video_path)

    # sign recognition for each segments
    start_time = time.time()
    print("start recognizing")
    recognition_results = recognize_segments_in_video(pose_npy_path, segments, fps)
    end_time = time.time()

    # record processing time
    processing_time = end_time - start_time

    print(f"Processing time for {segment_txt}: {processing_time:.2f} seconds")
    weights_name = weights_path.split("/")[-1]
    # JSON results
    output_json_path = os.path.join(segment_txt.split(".txt")[0]+".json")
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(recognition_results, json_file, ensure_ascii=False, indent=4)

    print(f"Results saved to {output_json_path}")
    print(recognition_results)
    print("DONE")  # backend waits for this message

