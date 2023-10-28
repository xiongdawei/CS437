import asyncio
import time
from sense_hat import SenseHat


sense = SenseHat()


def display_n_tiles(r, g, b, n = 64):
    # Display n tiles together at once
    if n > 64:
        n = 64
    pixels = [[r, g, b] if i < n else [0, 0, 0] for i in range(64) ]
    sense.set_pixels(pixels)

def display_color(r, g, b):
    print("Displaying color: ", r, g, b)
    sense.clear((r, g, b))


# If new RSSI line is added to the CSV file in the past 3 seconds, display the color based on the average of last 3 RSSI value
# Otherwise, display black
async def display_rssi():
    n = 3
    # Reduce the brightness of the LEDs
    sense.low_light = True
    # Read the last 3 lines of the CSV file
    with open("IMU/rssi.csv", mode = "r") as f:
        lines = f.readlines()
        lines_of_data = len(lines) - 1
        if len(lines) < 2:
            sense.clear()
            return
        last_3_lines = lines[-min(lines_of_data, n):]
        # Get the last 3 RSSI values
        last_3_rssi = [float(line.split(",")[3]) for line in last_3_lines]
        # If the last RSSI value is added to the CSV file in the past 3 seconds, display the color based on the average of last 3 RSSI value
        if time.time() - float(last_3_lines[0].split(",")[0]) < 2:
            avg_rssi = sum(last_3_rssi) / len(last_3_rssi)
            # Display RSSI value within range (-75, -25) as color from (255, 0, 0) to (255, 255, 0)
            # Display RSSI value within range (-25, 0) as color from (255, 255, 0) to (0, 255, 0)
            if -75 > avg_rssi:
                r, g, b = 0, 0, 0
            elif -75 < avg_rssi <= -50:
                r = 255
                g = min(int(255 * (avg_rssi + 75) / 50), 255)
                b = 0
            elif -50 < avg_rssi:
                r = min(int(255 * (-1 * avg_rssi) / 25), 255)
                g = 255
                b = 0
            display_n_tiles(r, g, b, max(avg_rssi + 75, 0))
        else:
            sense.clear()


async def display_rssi_color_loop(collection_time: int):
    start = time.time()
    while (time.time() - start) < collection_time:
        await display_rssi()


def display_rssi_color(collection_time: int):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(display_rssi_color_loop(collection_time))
