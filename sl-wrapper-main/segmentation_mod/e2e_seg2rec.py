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

    # 시간 측정
    start_time = time.time()
    # run video_to_pose

    subprocess.run(
        ["video_to_pose", "-i", video_file, "--format", "mediapipe", "-o", f"{output_name}.pose"],
        check=True,
    )

    # run segmentation
    subprocess.run(
        [
            "python3",
            "/Users/zzenninkim/Documents/Research/sl-wrapper-main/segmentation_mod/pose_to_segments/bin.py",
            "-i",
            f"{output_name}.pose",
            "-o",
            f"{output_name}.eaf",
            "--video",
            video_file,
        ],
        check=True,
    )
    os.system("video_to_pose -i \"{}\" --format mediapipe -o \"{}.pose\"".format(video_file, output_name))
    os.system("/Users/zzenninkim/Documents/Research/sl-wrapper-main/segmentation_mod/pose_to_segments/bin.py -i \"{}.pose\" -o \"{}.eaf\" --video \"{}\"".format(output_name, output_name, video_file))

    # 시간 측정 종료
    elapsed_time = time.time() - start_time

    output_eaf = Eaf(f"{output_name}.eaf")
    return output_eaf, elapsed_time

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--video', required=True, type=str, help='video path')

    return parser.parse_args()

if __name__ == "__main__":
    # 다음엔 frame 처리된거 읽을 수 있도록 해야함
    #video_path = "/Users/zzenninkim/Documents/Research/sl-wrapper-main/60085579467325-APPLE.mp4"
    args = get_args()
    video_path = args.video


    filename =  basename(video_path)
    output_file = os.path.splitext(video_path)[0] + '.txt'
    x, elapsed_time = segment_sign_video(video_path)


    # annotations 열어서 시작지점, 끝 지점 알게하기
    annotations = x.get_annotation_data_for_tier("SIGN")
    print("total segments: ", len(annotations))
    with open(output_file, 'w') as file:
        for annotation in annotations:
            start_time, end_time, value = annotation
            start_time_sec = start_time / 1000  # 밀리초를 초 단위로 변환
            end_time_sec = end_time / 1000  # 밀리초를 초 단위로 변환
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
