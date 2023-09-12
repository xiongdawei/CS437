from sense_hat import SenseHat

from time import sleep

sense = SenseHat()
sense.clear()

color = (255,0,0)
sense.show_pixel(3,5,color)

while True:
    for event in sense.stick.get_events():
        if event.action == "pressed":
            sense.clear()
        if event.direction == "up":
            sense.clear(color)
        elif event.direction == "down":
            sense.clear()
        elif event.direction == "left":
            sense.clear()
        elif event.direction == "right":
            sense.clear()
        elif event.direction == "middle":
            sense.clear()
        else:
            pass


