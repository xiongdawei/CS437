import csv
import pandas as pd
import matplotlib.pyplot as plt

# Load the raw data from the CSV file
csv_filename = "accelerometer_data.csv"
df = pd.read_csv(csv_filename)

# Calculate a moving average (e.g., window size of 5)
window_size = 5
df['X_smooth'] = df['X'].rolling(window=window_size).mean()
df['Y_smooth'] = df['Y'].rolling(window=window_size).mean()
df['Z_smooth'] = df['Z'].rolling(window=window_size).mean()

# Create a time vs. X, Y, Z plot
plt.figure(figsize=(12, 6))
plt.plot(df['Time (s)'], df['X'], label='X (Raw)')
plt.plot(df['Time (s)'], df['Y'], label='Y (Raw)')
plt.plot(df['Time (s)'], df['Z'], label='Z (Raw)')

# Create a time vs. smoothed X, Y, Z plot
plt.plot(df['Time (s)'], df['X_smooth'], label='X (Smoothed)')
plt.plot(df['Time (s)'], df['Y_smooth'], label='Y (Smoothed)')
plt.plot(df['Time (s)'], df['Z_smooth'], label='Z (Smoothed)')

plt.xlabel("Time (s)")
plt.ylabel("Acceleration")
plt.legend()
plt.title("Accelerometer Data")
plt.grid(True)
plt.show()
