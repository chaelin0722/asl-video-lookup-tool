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
src_path = '/Users/zzenninkim/dataset/ASL_Citizen/videos/'
dst_path = '/Users/zzenninkim/dataset/ASL_Citizen/npys/'
data_csv = '/Users/zzenninkim/dataset/ASL_Citizen/splits/train_23.csv'  # ← Update this with your actual file

with open(data_csv, 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip header

    count_f = 0
    start = timer()

    for row in reader:
        video_filename = row[1]  # From 'Video file' column
        video_path = os.path.join(src_path, video_filename)

        # Output filename based on original name
        output_filename = os.path.splitext(video_filename)[0] + '.npy'
        output_path = os.path.join(dst_path, output_filename)

        if os.path.exists(output_path):
            print(f"{output_path} exists, pass")
            continue

        with mp_holistic.Holistic(static_image_mode=False, min_detection_confidence=0.5) as holistic:
            video = cv2.VideoCapture(video_path)
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            feature = np.zeros((total_frames, 543, 2))
            count = 0
            success = True

            while success:
                success, image = video.read()
                if success:
                    results = holistic.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

                    for i in range(33):
                        if results.pose_landmarks:
                            feature[count][i] = [results.pose_landmarks.landmark[i].x,
                                                 results.pose_landmarks.landmark[i].y]

                    for i in range(21):
                        if results.right_hand_landmarks:
                            feature[count][33 + i] = [results.right_hand_landmarks.landmark[i].x,
                                                      results.right_hand_landmarks.landmark[i].y]
                        if results.left_hand_landmarks:
                            feature[count][54 + i] = [results.left_hand_landmarks.landmark[i].x,
                                                      results.left_hand_landmarks.landmark[i].y]

                    if results.face_landmarks:
                        for i in range(468):
                            feature[count][75 + i] = [results.face_landmarks.landmark[i].x,
                                                      results.face_landmarks.landmark[i].y]
                    count += 1

            np.save(output_path, feature)
            print(f"{output_path} saved")
            count_f += 1
            if count_f % 10 == 0:
                end = timer()
                print(f"Processed {count_f} videos in {end - start:.2f} seconds.")
                start = end