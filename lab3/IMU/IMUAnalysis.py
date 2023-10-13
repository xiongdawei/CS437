import numpy as np
import time
from datetime import datetime,date
import matplotlib.pyplot as plt
import pandas as pd
from scipy.interpolate import griddata


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


def read_accelerometer_data(df):
    timestamp = df['timestamp']
    x_axis=df['x']
    y_axis=df['y']
    z_axis=df['z']
    return timestamp, x_axis, y_axis, z_axis


def plot_raw_acceleration(timestamp, x_axis, y_axis, z_axis):
    plt.plot(timestamp, x_axis, label="X-axis Raw Acceleration")
    plt.plot(timestamp, y_axis, label="Y-axis Raw Acceleration")
    plt.plot(timestamp, z_axis, label="Z-axis Raw Acceleration")
    plt.legend(loc="upper left")
    plt.ylabel("Raw Acceleration in m/s^2")
    plt.xlabel("Timestamp")
    plt.show()

def plot_calibrated_acceleration(timestamp, x_axis, y_axis, z_axis):
    plt.plot(timestamp, x_axis, label="X-axis Caliberated Acceleration")
    plt.plot(timestamp, y_axis, label="Y-axis Caliberated Acceleration")
    plt.plot(timestamp, z_axis, label="Z-axis Caliberated Acceleration")
    plt.legend(loc="upper left")
    plt.ylabel("Caliberated Acceleration in m/s^2")
    plt.xlabel("Timestamp")
    plt.show()

def calibrate_acceleration_data(timestamp, x_axis, y_axis, z_axis):
    ## caliberate x,y,z to reduce the bias in accelerometer readings. Subtracting it from the mean means that in the absence of motion, the accelerometer reading is centered around zero to reduce the effect of integrigation drift or error.
    ## change the upper and lower bounds for computing the mean where the RPi is in static position at the begining of the experiment (i.e. for the first few readings). You can know these bounds from the exploratory plots above.
    x_calib_mean = np.mean(x_axis[10:100])
    x_calib = x_axis - x_calib_mean
    x_calib = x_calib[:]

    y_calib_mean = np.mean(y_axis[10:100])
    y_calib = y_axis - y_calib_mean
    y_calib = y_calib[:]

    z_calib_mean = np.mean(y_axis[10:1000])
    z_calib = z_axis - z_calib_mean
    z_calib = z_calib[:]

    timestamp = timestamp[:]
    return timestamp, x_calib, y_calib, z_calib

def read_joystick_data():
    with open("joystick.csv", "r") as f:
        joystick_data = f.readlines()
        # joystick_data: [timestamp, direction]
        # Group by direction
        up_down = []
        left_right = []
        for data in joystick_data:
            direction = data.split(",")[1].strip()
            print(direction)
            if direction == "up" or direction == "down":
                up_down.append(data)
            elif direction == "left" or direction == "right":
                left_right.append(data)
    return up_down, left_right

#print("Check if lengths of each vector are same for tracking time", len(timestamp), len(x_calib), len(y_calib), len(z_calib))
def calculate_velocity_and_position(timestamp, x_calib, y_calib, z_calib):
    # Find sampling time:
    dt = (timestamp[len(timestamp)-1] - timestamp[0]) / len(timestamp)

    grid_size = 1.22
    landmark_x = 0
    landmark_y = 0

    up_down, left_right = read_joystick_data()
    # Find index in timestamp that fits in each timestamp in joystick_data
    up_down_index = []
    left_right_index = []
    for data in up_down:
        up_down_index.append(np.argmin(np.abs(timestamp - float(data.split(",")[0]))))
    for data in left_right:
        left_right_index.append(np.argmin(np.abs(timestamp - float(data.split(",")[0]))))

    ## Computing Velocity and Position along Y Axis:
    y_vel = [0]
    for i in range(len(y_calib)-1):
        # dt = (timestamp[i+1] - timestamp[i])
        y_vel.append(y_vel[-1] + dt * y_calib[i])
    x_vel = [0]
    for i in range(len(x_calib)-1):
        # dt = (timestamp[i+1] - timestamp[i])
        x_vel.append(x_vel[-1] + dt * x_calib[i])

    y = [0]
    x = [0]
    up_down_idx = 0
    left_right_idx = 0
    for i in range(len(y_vel)-1):
        if up_down_idx < len(up_down_index) and i == up_down_index[up_down_idx]:
            direction = up_down[up_down_idx].split(",")[1].strip()
            if direction == "up":
                landmark_y += grid_size
                y[-1] = landmark_y
                x[-1] = landmark_x
                print(f"Direction UP set landmark to ({landmark_x}, {landmark_y})")
            elif direction == "down":
                landmark_y -= grid_size
                y[-1] = landmark_y
                x[-1] = landmark_x
                print(f"Direction DOWN set landmark to ({landmark_x}, {landmark_y})")
            up_down_idx += 1
        if left_right_idx < len(left_right_index) and i == left_right_index[left_right_idx]:
            direction = left_right[left_right_idx].split(",")[1].strip()
            if direction == "left":
                landmark_x -= grid_size
                x[-1] = landmark_x
                y[-1] = landmark_y
                print(f"Direction LEFT set landmark to ({landmark_x}, {landmark_y})")
            elif direction == "right":
                landmark_x += grid_size
                x[-1] = landmark_x
                y[-1] = landmark_y
                print(f"Direction RIGHT set landmark to ({landmark_x}, {landmark_y})")
            left_right_idx += 1
        y.append(y[-1] + dt * y_vel[i])
        x.append(x[-1] + dt * x_vel[i])

    ## Integrations along X axis

    ## Integrations along Z axis:
    z_vel = [0]
    for i in range(len(z_calib)-1):
        # dt = (timestamp[i+1] - timestamp[i])
        z_vel.append(z_vel[-1] + dt * z_calib[i])

    z = [0]
    for i in range(len(z_vel)-1):
        # dt = (timestamp[i+1] - timestamp[i])
        z.append(z[-1] + dt * z_vel[i])

    print(landmark_x, landmark_y)
    return timestamp, x_vel, y_vel, z_vel, x, y, z


def plot_velocity_and_position(timestamp, x_vel, y_vel, z_vel, x, y, z):
    # Subplotting velocity and position along X and Y axis
    plt.subplot(2, 1, 1)
    plt.plot(x_vel, label="X-axis velocity")
    plt.plot(y_vel, label="Y-axis velocity")
    plt.legend(loc="upper left")
    plt.ylabel("Velocity in m/s")
    plt.xlabel("# of Samples")
    ## Plot X and Y positions with respect to time:
    plt.subplot(2, 1, 2)
    plt.plot(timestamp.to_numpy(),x, label="X positions", c="red")
    plt.plot(timestamp.to_numpy(),y, label="Y positions", c="green")
    plt.legend(loc="upper left")
    plt.xlabel("Timestamp (seconds)")
    plt.ylabel("Positions (m)")
    plt.show()


def plot_color_coded_location(timestamp, x, y, rssi):
    # Draw a plot with two scatter line (timestamp, x) and (timestamp, y) within same plot with different marker and with RSSI as color code for points
    # RSSI color code should have a range: -75 to -10
    # Returns a scatter plot
    plt.scatter(x, y, c=rssi, marker='o')
    plt.xlabel('X position')
    plt.ylabel('Y position')
    plt.legend(['x', 'y'])

    # Plot the point with highest RSSI value, label it
    max_rssi_index = rssi.idxmax()
    max_rssi_x = x[max_rssi_index]
    max_rssi_y = y[max_rssi_index]
    plt.scatter(max_rssi_x, max_rssi_y, c='red', marker='x')
    plt.annotate('max RSSI', (max_rssi_x, max_rssi_y))

    # # Put (x, y, RSSI) together
    # x = np.array(x)
    # y = np.array(y)
    # rssi = np.array(rssi)
    # data = np.array([x, y, rssi]).T
    # x_min, x_max = x.min(), x.max()
    # y_min, y_max = y.min(), y.max()
    # x_grid = np.linspace(x_min, x_max, 20)
    # y_grid = np.linspace(y_min, y_max, 20)
    
    # Divide the (x, y) space into 20x20 grids
    x = np.array(x)
    y = np.array(y)
    x_min, x_max = x.min(), x.max()
    y_min, y_max = y.min(), y.max()
    x_grid = np.linspace(x_min, x_max, 20)
    y_grid = np.linspace(y_min, y_max, 20)

    # Find index in array x that fits in each x_grid
    x_grid_index = np.digitize(x, x_grid, right=True) - 1
    y_grid_index = np.digitize(y, y_grid, right=True) - 1

    # Calculate the average RSSI for each grid. Each grid is based on x and y axis.
    rssi_grid = [[[] for i in range(20)] for j in range(20)]
    for i in range(len(x)):
        rssi_grid[y_grid_index[i]][x_grid_index[i]].append(rssi[i])
    for i in range(20):
        for j in range(20):
            rssi_grid[i][j] = np.mean(rssi_grid[i][j])
    rssi_grid = np.array(rssi_grid)
    rssi_grid = np.nan_to_num(rssi_grid)

    # Get the (x, y) coordinate for each value in rssi_grid
    x_grid, y_grid = np.meshgrid(x_grid, y_grid)

    # Plot scatter plot with color code in rssi_grid. Only plot the points with non-zero RSSI value
    # plt.scatter(x_grid[rssi_grid != 0], y_grid[rssi_grid != 0], c=rssi_grid[rssi_grid != 0], marker='o')

    # Plot the point with highest non-zero RSSI value, label it
    # Convert zero values in rssi_grid to -200
    rssi_grid[rssi_grid == 0] = -200
    max_rssi_grid_index = np.unravel_index(np.argmax(rssi_grid, axis=None), rssi_grid.shape)
    max_rssi_grid_x = x_grid[max_rssi_grid_index]
    max_rssi_grid_y = y_grid[max_rssi_grid_index]
    plt.scatter(max_rssi_grid_x, max_rssi_grid_y, c='red', marker='x')
    plt.annotate('grid RSSI', (max_rssi_grid_x, max_rssi_grid_y))

    # Plot True label
    # Read from joystick.csv file, find the (x, y) coordinate for the timestamp
    # with open("joystick.csv", "r") as f:
    #     joystick_data = f.readline()
    # joystick_timestamp = float(joystick_data)
    # joystick_index = np.argmin(np.abs(timestamp - joystick_timestamp))
    # joystick_x = x[joystick_index]
    # joystick_y = y[joystick_index]
    # plt.scatter(joystick_x, joystick_y, c='green', marker='x')
    # plt.annotate('true label', (joystick_x, joystick_y))

    
    ### Postlab 2
    points = []
    data = []
    neededPoints = []
    for i in range(len(rssi_grid)):
        for j in range(len(rssi_grid[0])):
            if rssi_grid[i][j] == -60:
                neededPoints.append((i,j))
            else:
                data.append(rssi_grid[i][j])
                points.append((i,j))
    for (x,y) in neededPoints:
        outputValue = float(griddata(points=points,values=data, xi=(x,y), method="linear"))
        rssi_grid[x][y] = outputValue

    # Plot the point with highest non-zero RSSI value, label it
    # Convert zero values in rssi_grid to -200
    rssi_grid[rssi_grid == 0] = -200
    max_rssi_grid_index = np.unravel_index(np.argmax(rssi_grid, axis=None), rssi_grid.shape)
    max_rssi_grid_x = x_grid[max_rssi_grid_index]
    max_rssi_grid_y = y_grid[max_rssi_grid_index]
    plt.scatter(max_rssi_grid_x, max_rssi_grid_y, c='red', marker='x')
    plt.annotate('spatial RSSI', (max_rssi_grid_x, max_rssi_grid_y))

    plt.show()



if __name__ == "__main__":
    merged_data = merge_data(imu_data_fname, rssi_data_fname)
    # merged_data.to_csv("baseline.csv", index=False)

    timestamp, x_axis, y_axis, z_axis = read_accelerometer_data(merged_data)
    # plot_raw_acceleration(timestamp, x_axis, y_axis, z_axis)

    timestamp, x_calib, y_calib, z_calib = calibrate_acceleration_data(timestamp, x_axis, y_axis, z_axis)
    # plot_calibrated_acceleration(timestamp, x_calib, y_calib, z_calib)

    timestamp, x_vel, y_vel, z_vel, x, y, z = calculate_velocity_and_position(timestamp, x_calib, y_calib, z_calib)
    # plot_velocity_and_position(timestamp, x_vel, y_vel, z_vel, x, y, z)

    plot_color_coded_location(timestamp, x, y, merged_data['rssi'])
    # plot_spatial_interpolation(x, y, merged_data['rssi'])
