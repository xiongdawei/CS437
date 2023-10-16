import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("TkAgg")  # use TkAgg backend to prevent segmentation fault
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Load IMU data from CSV
data = pd.read_csv('imu_data7.csv')

# Extract relevant accelerometer data (assuming columns 'accel_x', 'accel_y', 'accel_z')
data = data[50:]
accel_x = data['Accel_x']
accel_y = data['Accel_y']
accel_z = data['Accel_z']

# Extract relevant gyroscope data (assuming columns 'gyro_x', 'gyro_y', 'gyro_z')
gyro_x = data['Gyro_x']
gyro_y = data['Gyro_y']
gyro_z = data['Gyro_z']



# Combine the three accelerometer components to obtain a single magnitude
accel_magnitude = np.sqrt(accel_x**2 + accel_y**2 + accel_z**2)

# Apply a low-pass filter to reduce noise (you can adjust the filter parameters)
from scipy.signal import butter, lfilter

def butter_lowpass(cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

# Define filter parameters
cutoff_freq = 5.0  # Adjust the cutoff frequency as needed
fs = 20.0  # Adjust the sampling frequency as needed

# Apply the low-pass filter to the acceleration magnitude
filtered_accel_magnitude = butter_lowpass_filter(accel_magnitude, cutoff_freq, fs)

# Find peaks in the filtered data
threshold = 0.3  # Adjust the threshold as needed
peaks, _ = find_peaks(filtered_accel_magnitude, height=threshold)  # Adjust 'threshold' based on your data
num_steps = len(peaks)
print(peaks)
# give me the timestamp when there is a peak
peaks_timestamp = []
peaks_accel_magnitude = []
a = data['timestamp'].to_numpy()
for i in peaks:
    peaks_timestamp.append(a[i])
    peaks_accel_magnitude.append(filtered_accel_magnitude[i])
df = pd.DataFrame({'timestamp': peaks_timestamp, 'accel_magnitude': peaks_accel_magnitude})
df.to_csv('peaks.csv', index=False)




# Plot the data and highlight the detected peaks
plt.figure(figsize=(12, 6))
plt.plot(filtered_accel_magnitude)
plt.plot(peaks, filtered_accel_magnitude[peaks], "x", label="steps")
# plot x, y direction acceleration
# plt.plot(gyro_x, label="gyro_x")
# plt.plot(gyro_y, label="gyro_y")
plt.legend()
plt.title("Step Detection with IMU Data / " + "Number of steps detected: " + str(num_steps))
plt.xlabel("Time")
plt.ylabel("Filtered Acceleration Magnitude")
plt.show()



