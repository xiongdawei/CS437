from sense_hat import SenseHat
import csv
import time

sense = SenseHat()

# Create a CSV file for saving data
csv_filename = "accelerometer_data.csv"

# Record data for 10 seconds
duration = 10  # seconds
start_time = time.time()
end_time = start_time + duration

with open(csv_filename, mode='w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Time (s)", "X", "Y", "Z"])

    while time.time() < end_time:
        acceleration = sense.get_accelerometer_raw()
        timestamp = time.time() - start_time
        x, y, z = acceleration['x'], acceleration['y'], acceleration['z']
        csv_writer.writerow([timestamp, x, y, z])
        time.sleep(0.1)  # Adjust the sampling rate as needed

print("Data collection complete. Saved to", csv_filename)

