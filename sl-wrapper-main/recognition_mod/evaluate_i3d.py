import csv

# 입력 파일 경로
txt_file_path = "/Users/zzenninkim/dataset/ASL_Citizen/splits/annotation.txt"  # txt 파일 경로
csv_file_path = "/Users/zzenninkim/dataset/ASL_Citizen/splits/output_gloss.csv"  # 생성할 CSV 파일 경로

# 데이터 저장을 위한 set (중복 방지)
data_set = set()

# txt 파일 읽기 및 파싱
with open(txt_file_path, "r", encoding="utf-8") as file:
    for line in file:
        line = line.strip()  # 앞뒤 공백 제거
        if not line:
            continue  # 빈 줄 건너뛰기

        # 3519807015280918-STAND-UP,2256 예를 들어 이렇게 생겼음

        left, right = line.split(",")  # , 기준으로 나누기
        gloss = left[len(left.split("-")[0])+1:]

        if gloss.startswith("seed"):
            gloss = gloss[4:]  # "seed" 제거
        gloss = gloss.replace(" ", "")
        gloss = gloss.replace("_", "")
        # 알파벳만 남기기
        index = int(right)  # 숫자로 변환

        # 데이터 추가 (set을 사용하여 중복 제거)
        data_set.add((index, gloss))

# set을 리스트로 변환 후 Index 기준으로 정렬
data_list = sorted(data_set, key=lambda x: x[0])

# CSV 파일 저장
with open(csv_file_path, "w", encoding="utf-8", newline="") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["Index", "Gloss"])  # 헤더 추가
    writer.writerows(data_list)  # 데이터 추가

print(f"CSV 파일이 생성되었습니다: {csv_file_path}")