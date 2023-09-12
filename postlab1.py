from sense_hat import SenseHat

from time import sleep

sense = SenseHat()
sense.clear()

color = (255,0,0)

x = 3
y = 5
sense.set_pixel(x, y,color)

while True:
    for event in sense.stick.get_events():
        if event.action == "pressed":
            sense.clear()
            break
        if event.direction == "up":
            sense.clear()
            for i in range(0, y):
                sense.set_pixel(x, i, color)
            sense.clear(color)
        elif event.direction == "down":
            sense.clear()
            for i in range(y, 8):
                sense.set_pixel(x, i, color)
        elif event.direction == "left":
            sense.clear()
            for i in range(0, x):
                sense.set_pixel(i, y, color)
        elif event.direction == "right":
            sense.clear()
            for i in range(x, 8):
                sense.set_pixel(i, y, color)
        else:
            pass


