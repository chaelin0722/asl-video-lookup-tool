import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
 
file_name = "dir of file name"
 
save_path = "dir to save npy"

# 27개 keypoint index
keypoints = [0, 2, 5, 11, 12, 13, 14, 33, 37, 38, 41, 42, 45, 46,
             49, 50, 53, 54, 58, 59, 62, 63, 66, 67, 70, 71, 74]

data = np.load(file_name)

data = data[:, keypoints, :]  # shape: (T, 27, 2)
num_frames = data.shape[0]
# shape = (70, 543, 2)

# set plot
fig, ax = plt.subplots(figsize=(6,6))
scatter = ax.scatter([], [], s=10)
ax.set_xlim(-1,1)
ax.set_ylim(-1,1)
ax.set_title("Pose Keypoints Animation")
ax.grid(True)

def update(frame_idx):
    frame = data[frame_idx]
    x = frame[:, 0]
    y = -frame[:, 1]  # 보기 좋게 뒤집기
    scatter.set_offsets(np.c_[x, y])
    ax.set_title(f"Frame {frame_idx + 1}/{num_frames}")
    return scatter,

# creat animation
ani = FuncAnimation(fig, update, frames=num_frames, interval=50, blit=True)

# set save
writer = FFMpegWriter(fps=20, metadata=dict(artist='Chaelin'), bitrate=1800)
ani.save(save_path, writer=writer)

print(f"Saved animation to {save_path}")
