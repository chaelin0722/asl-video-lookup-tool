import subprocess
import os

# 비디오 파일 경로와 출력 경로 설정
input_video_path = "/Users/zzenninkim/Documents/Research/sl-wrapper-main/Animal_Narrative.mp4"
output_folder_path = "/Users/zzenninkim/Documents/Research/sl-wrapper-main/clips/"

# 시작 시간 설정
start_time = 3  # 시작 시점 (3초)
#durations = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95]
durations = []
for i in range(8, 100, 5):
    durations.append(i)
'''
# 출력 폴더가 없으면 생성
if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)

# 각 길이에 맞게 비디오 자르기
for duration in durations:
    output_path = os.path.join(output_folder_path, f"clip_{duration-3}s.mp4")

    # ffmpeg 명령어 구성
    command = [
        "ffmpeg",
        "-i", input_video_path,
        "-ss", str(start_time),
        "-t", str(duration),
        "-c", "copy",  # 인코딩 없이 복사
        output_path
    ]

    # ffmpeg 실행
    try:
        subprocess.run(command, check=True)
        print(f"Saved: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while processing {duration} seconds clip: {e}")
'''


# file trim!
output_folder = "/Users/zzenninkim/Documents/Research/sl-wrapper-main/clips"
# 폴더 내의 mp4 파일 목록 가져오기
file_list = [f for f in os.listdir(output_folder_path) if f.endswith('.mp4')]

# 각 파일을 트리밍하여 저장
for file_name in file_list:
    input_path = os.path.join(output_folder_path, file_name)
    output_path = os.path.join(output_folder, f"trimmed_{file_name}")

    # ffmpeg 명령어 생성 (앞의 3초를 제거)
    command = [
        'ffmpeg',
        '-ss', '3',  # 시작 시간을 3초로 설정하여 앞의 3초를 제거
        '-i', input_path,  # 입력 파일
        '-c', 'copy',
        output_path
    ]

    # ffmpeg 명령어 실행
    subprocess.run(command)
