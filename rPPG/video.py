import scipy.io as sio
import numpy as np
import matplotlib.pyplot as plt

sample_file = sio.loadmat('./mmpd/p6_0.mat')
print(sample_file.keys())

video = sample_file['video']
gt = sample_file['GT_ppg']

#print(sample_file['video'])

import cv2
import numpy as np

# 假设 data 是您的 (1800, 80, 60, 3) 形状数组
# data = np.array([...])
video = (video * 255).astype(np.uint8)
# 设置视频保存路径和编码器
output_file = 'output.avi'  # AVI 格式
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # 选择编码器
fps = 30  # 帧率
frame_size = (60, 80)  # 帧大小

# 创建视频编写器
out = cv2.VideoWriter(output_file, fourcc, fps, frame_size)

# 写入视频帧
for i in range(video.shape[0]):
    frame = video[i]  # 获取一帧
    frame = cv2.resize(frame, frame_size)  # 如果需要，调整帧大小
    out.write(frame)  # 写入帧


import os

# Define the directory path
dir_path = './mmpd'

# Loop over all files in the directory
for filename in os.listdir(dir_path):
    # Check if the file is a regular file (not a directory)
    if os.path.isfile(os.path.join(dir_path, filename)):
        # Do something with the file
        sample_file = sio.loadmat('./mmpd/' + filename)
        print(filename)
        video = sample_file['video']
        video = (video * 255).astype(np.uint8)
        output_file = './mmpd/video/'+ filename +'.avi'
        fourcc = cv2.VideoWriter_fourcc(*'XVID')  # 选择编码器
        fps = 30  # 帧率
        frame_size = (60, 80)  # 帧大小

        out = cv2.VideoWriter(output_file, fourcc, fps, frame_size)

        # 写入视频帧
        for i in range(video.shape[0]):
            frame = video[i]  # 获取一帧
            frame = cv2.resize(frame, frame_size)  # 如果需要，调整帧大小
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(frame)  # 写入帧

        out.release()



# 释放编写器
