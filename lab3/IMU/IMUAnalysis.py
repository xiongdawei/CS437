import numpy as np
import time
from datetime import datetime,date
import matplotlib.pyplot as plt
import pandas as pd


imu_data_fname = "imu_data.csv"
rssi_data_fname = "rssi.csv"
filename = "data.csv"

# Merge imu data and rssi data based on timestamp
def merge_data(imu_data_fname, rssi_data_fname):
    # Merge IMU data and RSSI data files based on their timestamp
    # For each timestamp in IMU data, find the closest timestamp in RSSI data
    # Returns a dataframe with merged data
    imu_data = pd.read_csv(imu_data_fname)
    rssi_data = pd.read_csv(rssi_data_fname)
    merged_data = pd.DataFrame(columns=['timestamp', 'x', 'y', 'z', 'rssi'])
    for index, row in imu_data.iterrows():
        imu_timestamp = row['timestamp']
        rssi_timestamp = rssi_data['timestamp'].sub(imu_timestamp).abs().idxmin()
        merged_data = merged_data.append({'timestamp': imu_timestamp, 'x': row['Accel_x'], 'y': row['Accel_y'], 'z': row['Accel_z'], 'rssi': rssi_data.loc[rssi_timestamp]['rssi']}, ignore_index=True)
    return merged_data

merged_data = merge_data(imu_data_fname, rssi_data_fname)
# Subtract base timestamp from all timestamps
merged_data['timestamp'] = merged_data['timestamp'].sub(merged_data['timestamp'].min())

def plot_scatter(merged_data):
    # Draw a plot with two scatter line (timestamp, x) and (timestamp, y) within same plot with different marker and with RSSI as color code for points
    # RSSI color code should have a range: -75 to -10
    # Returns a scatter plot
    plt.scatter(merged_data['timestamp'], merged_data['x'], c=merged_data['rssi'], marker='o')
    plt.scatter(merged_data['timestamp'], merged_data['y'], c=merged_data['rssi'], marker='x')
    plt.xlabel('Timestamp')
    plt.ylabel('Acceleration')
    plt.legend(['x', 'y'])
    plt.show()


plot_scatter(merged_data)
exit(0)

df = pd.read_csv(filename, header=None)
df=df.dropna()

timestamp = df[0]

timestamps2=df[1]
x_axis=df[2]
y_axis=df[3]
z_axis=df[4]
plt.plot(x_axis,  label="X-axis Raw Acceleration")
plt.plot(y_axis,  label="Y-axis Raw Acceleration")
plt.plot(z_axis,  label="Z-axis Raw Acceleration")
plt.legend(loc="upper left")
plt.ylabel("Raw Acceleration in m/s^2")
plt.xlabel("Number of Data Points")
plt.show()
### CALIBERATION
x_calib_mean = np.mean(x_axis[10:100])
## caliberate x,y,z to reduce the bias in accelerometer readings. Subtracting it from the mean means that in the absence of motion, the accelerometer reading is centered around zero to reduce the effect of integrigation drift or error.
## change the upper and lower bounds for computing the mean where the RPi is in static position at the begining of the experiment (i.e. for the first few readings). You can know these bounds from the exploratory plots above.
x_calib = x_axis - x_calib_mean
x_calib = x_calib[:]
timestamp = timestamp[:]

y_calib_mean = np.mean(y_axis[10:100])
y_calib = y_axis - y_calib_mean
y_calib = y_calib[:]
timestamp = timestamp[:]


z_calib_mean = np.mean(y_axis[10:1000])
z_calib = z_axis - z_calib_mean
z_calib = z_calib[:]
timestamp = timestamp[:]

plt.plot(x_calib, label="X-axis Caliberated Acceleration")
plt.plot(y_calib, label="Y-axis Caliberated Acceleration")
plt.plot(z_axis, label="Z-axis Caliberated Acceleration")
plt.legend(loc="upper left")
plt.ylabel("Caliberated Acceleration in m/s^2")
plt.xlabel("Number of Data Points")
plt.show()


#print("Check if lengths of each vector are same for tracking time", len(timestamp), len(x_calib), len(y_calib), len(z_calib))
# Find sampling time:
dt = (timestamp[len(timestamp)-1] - timestamp[0]) / len(timestamp)

## Computing Velocity and Position along Y Axis:
y_vel = [0]
for i in range(len(y_calib)-1):
    y_vel.append(y_vel[-1] + dt * y_calib[i])



y = [0]

for i in range(len(y_vel)-1):
    y.append(y[-1] + dt * y_vel[i])
    




## Integrations along X axis
x_vel = [0]
for i in range(len(x_calib)-1):
    x_vel.append(x_vel[-1] + dt * x_calib[i])

plt.plot(x_vel, label="X-axis velocity")
plt.plot(y_vel, label="Y-axis velocity")
plt.legend(loc="upper left")
plt.ylabel("Velocity in m/s")
plt.xlabel("# of Samples")
plt.show()

x = [0]

for i in range(len(x_vel)-1):
    x.append(x[-1] + dt * x_vel[i])
    



## Integrations along Z axis:

z_vel = [0]
for i in range(len(z_calib)-1):
    z_vel.append(z_vel[-1] + dt * z_calib[i])

#plt.plot(z_vel)

z = [0]
plt.figure()
for i in range(len(z_vel)-1):
    z.append(z[-1] + dt * z_vel[i])
#plt.plot(z)

## Plot X and Y positions with respect to time:
plt.plot(timestamp.to_numpy(),x, label="X positions", c="red")
plt.plot(timestamp.to_numpy(),y, label="Y positions", c="green")
plt.legend(loc="upper left")
plt.xlabel("Timestamp (seconds)")
plt.ylabel("Positions (m)")
plt.show()


## Visualizing scatter plot in 2D


##
