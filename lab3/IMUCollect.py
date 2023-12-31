import asyncio
from sense_hat import SenseHat
import time
from datetime import datetime,date
import csv

path="/home/pi/CS437/lab3/IMU/"
sense=SenseHat()

timestamp_fname=datetime.now().strftime("%H:%M:%S")
sense.set_imu_config(True,True,True) ## Config the Gyroscope, Accelerometer, Magnetometer
# filename=path+timestamp_fname+".csv"
filename = "IMU/imu_data.csv"

def create_imu_file():
    with open(filename, "w") as f:
        f.write("timestamp,Accel_x,Accel_y,Accel_z,Gyro_x,Gyro_y,Gyro_z,Mag_x,Mag_y,Mag_z\n")


async def collect_imu_data():
    accel=sense.get_accelerometer_raw()  ## returns float values representing acceleration intensity in Gs
    gyro=sense.get_gyroscope_raw()  ## returns float values representing rotational intensity of the axis in radians per second
    mag=sense.get_compass_raw()  ## returns float values representing magnetic intensity of the ais in microTeslas

    timestamp=time.time()

    # Write data to file
    with open(filename, mode = "a", newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([timestamp, accel['x'], accel['y'], accel['z'], gyro['x'], gyro['y'], gyro['z'], mag['x'], mag['y'], mag['z']])

    return accel, gyro, mag, timestamp 


async def record_joystick():
    for event in sense.stick.get_events():
        if event.action =="pressed": ## check if the joystick was pressed
            if event.direction=="middle":
                sense.show_letter("M",text_colour=(255,255,255))
                return "middle"
            elif event.direction=="up":
                sense.show_letter("U",text_colour=(255,255,255))
                return "up"
            elif event.direction=="down":
                sense.show_letter("D",text_colour=(255,255,255))
                return "down"
            elif event.direction=="left":
                sense.show_letter("L",text_colour=(255,255,255))
                return "left"
            elif event.direction=="right":
                sense.show_letter("R",text_colour=(255,255,255))
                return "right"
    return ""
    

async def imu_collect_loop(collection_time: int):
    # Create a async coroutine that runs for 30 seconds
    start = time.time()
    location_marked = False
    while (time.time() - start) < collection_time:
        accel, gyro, mag, timestamp = await collect_imu_data()
        if not location_marked:
            if await record_joystick():
                location_marked = True
                with open("IMU/joystick.csv", mode = "w", newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow([timestamp])

def imu_collect(collection_time: int):
    # Create a loop that runs the async coroutine
    create_imu_file()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(imu_collect_loop(collection_time))
    # loop.close()

if __name__ == "__main__":
    imu_collect(20)
