import cv2
import mediapipe as mp
import numpy as np
import csv
from timeit import default_timer as timer
import os
# Initialize mediapipe drawing class - to draw the landmarks points.
mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

# Update paths here
src_path = "/Volumes/SeagateHub/ASLLVD/all_videos/"
dst_path = "/Volumes/SeagateHub/ASLLVD/all_npys/"
data_csv = "/Users/zzenninkim/dataset/ASLLRP/ASLLVD_FINAL_INFO.csv"

# example of data_csv
# User ID,Video Filename,Gloss Label,Start Frame,End Frame,Additional Info
# 1234,sign_00123.mp4,HELLO,0,60,info1
# 5678,sign_00456.mp4,THANKYOU,10,80,info2
# 9101,sign_00789.mp4,PLEASE,5,70,info3



with open(data_csv, 'r') as file:
    reader = csv.reader(file)
    count_f = 0
    start = timer()
    for row in reader:
        f = src_path + row[1]

        # if video not exists, pass
        if not os.path.exists(f):
            print(f"{f} not exists, pass")
            continue


        start_frame = int(row[3])
        end_frame = int(row[4])
        num_frames_to_process = end_frame - start_frame + 1

        # if npy exists, pass the extracting landmarks process
        check_f = dst_path + row[2].split(".")[0] + '.npy'
        if os.path.exists(check_f):
            print(f"{check_f} exists, pass")
            continue

        with mp_holistic.Holistic(
                static_image_mode=False, min_detection_confidence=0.5) as holistic:

            video = cv2.VideoCapture(f)
            total_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)

            all_feature = np.zeros((int(total_frames), 543, 2))

            feature = all_feature[start_frame:end_frame+1]

            # jump to start point
            video.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

            count = 0
            success = 1

            while success and count < num_frames_to_process:
                success, image = video.read()
                if not success:
                    break

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

            name = ''.join(row[2].split(".")[0])
            np.save(dst_path + name + '.npy', feature)

            print(f"{check_f} saved")
            count_f += 1
            if count_f % 10 == 0:
                end = timer()
                print(end - start)
                print(count_f)
                start = end