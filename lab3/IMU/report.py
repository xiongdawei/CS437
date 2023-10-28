import numpy as np
import time
from datetime import datetime,date
import matplotlib.pyplot as plt
import pandas as pd
from scipy.interpolate import griddata
from scipy.optimize import curve_fit

imu_data_fname = "imu_data.csv"
rssi_data_fname = "rssi.csv"
filename = "data.csv"
step_data_fname = "peaks.csv"



def read_step_data():
    with open(step_data_fname, "r") as f:
        step_data = f.readlines()[1:]
        # step_data: [timestamp, magnitude]
        step_index = []
        # Find index in IMU data timestamp that is closest to each timestamp in step_data
        # find max and min step magnitude
        max_mag = -1
        min_mag = 100000
        for data in step_data:
            magnitude = float(data.split(",")[1].strip())
            if magnitude > max_mag:
                max_mag = magnitude
            if magnitude < min_mag:
                min_mag = magnitude
    return step_data, max_mag, min_mag


def read_and_process_joystick_data():
    with open("joystick.csv", "r") as f:
        joystick_data = f.readlines()
        # joystick_data: [timestamp, direction]
        # Group by direction
        joystick_data = [data.split(",") for data in joystick_data]
    return joystick_data

def get_t_dt(step_data, max_mag, min_mag = 0.3, max_step_size = 0.8):
    # Get a sequence of (timestamp, d_t) for each step
    t_dt = []
    for data in step_data:
        timestamp = float(data.split(",")[0].strip())
        magnitude = float(data.split(",")[1].strip())
        # Normalize magnitude to [0, 1]
        magnitude = (magnitude - min_mag) / (max_mag - min_mag)
        # Map magnitude to step size
        step_size = (max_step_size - 0) * magnitude + 0
        t_dt.append((timestamp, step_size))
    return np.array(t_dt)


def get_t_x_y(t_dt, joystick_data):
    # t_dt: [timestamp, distance of step in meters at timestamp]
    # Get a sequence of (timestamp, x, y) for each step
    t_x_y = []
    x, y = 0, 0
    # (assumes t_dt is much longer than joystick_data)
    t_dt_idx = 0
    for direction_timestamp, direction in joystick_data:
        direction_timestamp = float(direction_timestamp)
        direction = direction.strip()
        while t_dt_idx < len(t_dt) and t_dt[t_dt_idx][0] < direction_timestamp:
            step_distance = t_dt[t_dt_idx][1]
            if direction == "up":
                y += step_distance
            elif direction == "down":
                y -= step_distance
            elif direction == "left":
                x -= step_distance
            elif direction == "right":
                x += step_distance
            t_x_y.append((t_dt[t_dt_idx][0], x, y))
            t_dt_idx += 1
    return np.array(t_x_y)

def plot_t_x_y(t_x_y):
    # t_x_y: [timestamp, x, y]
    # Scatter plot (x, y) coordinates
    plt.scatter(t_x_y[:,1], t_x_y[:,2])
    plt.show()

if __name__ == "__main__":
    step_data, max_mag, min_mag = read_step_data()
    print(max_mag, min_mag)

    t_dt = get_t_dt(step_data, max_mag, min_mag)
    print(t_dt)

    joystick_data = read_and_process_joystick_data()
    t_x_y = get_t_x_y(t_dt, joystick_data)

    plot_t_x_y(t_x_y)