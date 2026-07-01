import sys
import subprocess
import os


def convert_webm_to_mp4(webm_path):
    mp4_path = webm_path.replace(".webm", ".mp4")

    try:
        subprocess.run([
            "ffmpeg",
            "-y",  # overwrite
            "-i", webm_path,
            "-an",
            "-c:v", "libx264",
            "-preset", "fast",
            "-pix_fmt", "yuv420p",
            mp4_path
        ], check=True)
        print(mp4_path)
    except subprocess.CalledProcessError as e:
        print("Error during conversion:", e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_webm_to_mp4.py input.webm")
        sys.exit(1)

    convert_webm_to_mp4(sys.argv[1])

#python3 convert_webm_to_mp4.py /Users/zzenninkim/Documents/Research/asl-search-automation-main/src/tmp/video-1743621724427-220226286.webm /Users/zzenninkim/Documents/Research/asl-search-automation-main/src/tmp/video-1743621724427-220226286.mp4