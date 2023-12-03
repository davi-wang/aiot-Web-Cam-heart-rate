# read mat file
import scipy.io as sio
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import stft, find_peaks

sample_file = sio.loadmat('./mmpd/p6_0.mat')

gt = sample_file['GT_ppg']


with open('./mmpd/result/p6_0.txt', 'r') as file:
    loaded_numbers = []
    for line in file:
        try:
            # 尝试将行内容转换为整数
            number = float(line.strip())
        except ValueError:
            # 如果转换失败，使用0代替
            number = 0
        loaded_numbers.append(number)

print(loaded_numbers)


gt = gt.flatten()

fft_result = np.fft.fft(gt)

# 获取FFT结果的长度
n = gt.size

# 计算频率（假设采样频率为每秒30个点）
sample_rate = 30
freq = np.fft.fftfreq(n, d=1/sample_rate)

indices = np.where((freq >= 0.5) & (freq <= 3))
selected_freq = freq[indices]
selected_fft = fft_result[indices]

# 绘制FFT结果的幅度
plt.plot(selected_freq, np.abs(selected_fft))
plt.title('FFT of the Signal (0.5Hz to 3Hz)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.show()


x = range(1, 1801)
plt.plot(x,gt)
plt.show()