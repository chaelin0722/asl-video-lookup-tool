import os
from os.path import basename
import time
from pympi.Elan import Eaf


def segment_sign_video(video_file: str) -> Eaf:
    """
    TODO MB
    """
    file_name = os.path.basename(video_file)
    output_name = os.path.splitext(file_name)[0]

    # 시간 측정
    start_time = time.time()

    #os.system("video_to_pose -i \"{}\" --format mediapipe -o sign.pose".format(video_file))
    os.system("video_to_pose -i \"{}\" --format mediapipe -o \"{}.pose\"".format(video_file, output_name))
    os.system("/Users/zzenninkim/Documents/Research/sl-wrapper-main/segmentation_mod/pose_to_segments/bin.py -i \"{}.pose\" -o \"{}.eaf\" --video \"{}\"".format(output_name, output_name, video_file))

    # 측정종료
    elapsed_time = time.time() - start_time

    output_eaf = Eaf("{}.eaf".format(output_name))

    #os.system("rm \"sign.eaf\"")
    #os.system("rm \"sign.pose\"")

    return output_eaf, elapsed_time


if __name__ == "__main__":

    video_folder = "/Users/zzenninkim/Documents/Research/sl-wrapper-main/clips/"

    file_list = sorted([f for f in os.listdir(video_folder) if f.startswith("trimmed_")])
    times = []
    # 각 파일에 대해 처리하기
    for file_name in file_list:
        file_path = os.path.join(video_folder, file_name)
        output_file = os.path.splitext(file_name)[0] + '.txt'

        x, elapsed_time = segment_sign_video(file_path)

        # annotations 일어서 시작지점, 끝 지점 알게하기
        annotations = x.get_annotation_data_for_tier("SIGN")
        print("total segments: ", len(annotations))
        with open(output_file, 'w') as file:
            for annotation in annotations:
                start_time, end_time, value = annotation
                start_time_sec = start_time / 1000  # 밀리초를 초 단위로 변환
                end_time_sec = end_time / 1000  # 밀리초를 초 단위로 변환
                print(f"Start: {start_time_sec:.3f} sec, End: {end_time_sec:.3f} sec")
                file.write(f"Start: {start_time_sec:.3f} sec, End: {end_time_sec:.3f} sec\n")

        print(f"Segmentation took {elapsed_time:.3f} seconds for {file_name}")
        times.append((file_name, elapsed_time))

    output_time_file = "segment_time.txt"

    # 여기 잘 안되니 확인해보기
    with open(output_time_file, 'w') as time_file:
        for filename, time in times:
            file.write(f"{filename}, {time:.3f}")