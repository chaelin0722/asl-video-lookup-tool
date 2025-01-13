import os
import subprocess
from os.path import basename
import time
from pympi.Elan import Eaf
import argparse
#  os.system은 간단하지만 출력 캡처 및 에러 처리가 어렵다. 따라서
#  더 세부적인 제어가 가능하며 출력 및 오류처리가 쉬운 subprocess로 변경!
#
#

def segment_sign_video(video_file: str) -> Eaf:
    """
    TODO MB
    """
    file_name = os.path.basename(video_file)
    output_name = os.path.splitext(file_name)[0]
    print("start segmenting!", output_name)
    # check time
    start_time = time.time()
    # run video_to_pose
    print("run video_to_pose")
    subprocess.run(
        ["video_to_pose", "-i", video_file, "--format", "mediapipe", "-o", f"{output_name}.pose"],
        check=True,
    )

    # run segmentation
    print("run pose_to_segment")
    subprocess.run(
        [
            "python3",
            "/Users/zzenninkim/Documents/Research/sl-wrapper-main/segmentation_mod/pose_to_segments/bin.py",
            "--pose",
            f"{output_name}.pose",
            "--elan",
            f"{output_name}.eaf",
            "--video",
            video_file,
        ],
        check=True,
    )
    print("done pose_to_segment, done pose and eaf files")
    os.system("/Users/zzenninkim/Documents/Research/sl-wrapper-main/segmentation_mod/video_to_pose/bin.py -i \"{}\" --format mediapipe -o \"{}.pose\"".format(video_file, output_name))
    os.system("/Users/zzenninkim/Documents/Research/sl-wrapper-main/segmentation_mod/pose_to_segments/bin.py -i \"{}.pose\" -o \"{}.eaf\" --video \"{}\"".format(output_name, output_name, video_file))
    print("done all the segmenting files")
    # 시간 측정 종료
    elapsed_time = time.time() - start_time

    output_eaf = Eaf(f"{output_name}.eaf")
    return output_eaf, elapsed_time

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--video', required=True, type=str, help='video path')

    return parser.parse_args()

if __name__ == "__main__":
    #video_path = "/Users/zzenninkim/Documents/Research/sl-wrapper-main/60085579467325-APPLE.mp4"
    args = get_args()
    video_path = args.video


    filename =  basename(video_path)
    output_file = os.path.splitext(video_path)[0] + '.txt'
    x, elapsed_time = segment_sign_video(video_path)


    # annotations 열어서 시작지점, 끝 지점 알게하기
    annotations = x.get_annotation_data_for_tier("SIGN")
    print("total segments: ", len(annotations))
    padding = 0
    with open(output_file, 'w') as file:
        for annotation in annotations:
            start_time, end_time, value = annotation
            start_time_sec = start_time / 1000 # 밀리초를 초 단위로 변환
            end_time_sec = (end_time / 1000) + padding # 밀리초를 초 단위로 변환
            print(f"Start: {start_time_sec:.3f} sec, End: {end_time_sec:.3f} sec")
            file.write(f"Start: {start_time_sec:.3f} sec, End: {end_time_sec:.3f} sec\n")

    print(f"Segmentation took {elapsed_time:.3f} seconds for {filename}")

try:
    # run recognition model
    subprocess.run(
        [
                "python3",
                "/Users/zzenninkim/Documents/Research/sl-wrapper-main/recognition_mod/e2e_recognition.py",
                "--input_segtxt", output_file,
                "--video", video_path],

        check=True
    )


except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
    print(f"Output: {e.output}")
    print(f"Return code: {e.returncode}")




#video_path = "/Users/zzenninkim/Documents/Research/sl-wrapper-main/60085579467325-APPLE.mp4"
#segment_txt = "/Users/zzenninkim/Documents/Research/sl-wrapper-main/60085579467325-APPLE.txt"
