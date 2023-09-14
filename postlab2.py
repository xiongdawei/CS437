from sense_hat import SenseHat
from time import sleep
import math
import numpy as np
import matplotlib.pyplot as plt

sense = SenseHat()

sense.clear()


for i in range(600):
    temperature = sense.get_temperature()
    temp.append(temperature)
    sleep(0.05)
    
x = []
y1 = []
y2 = []
sum = 0
div = 40
for i in range(len(temp)):
    sum += temp[i]
    if (i+1) % div == 0:
        y1.append(temp[i])
        y2.append(sum/div)
        print(temp[i])
        print(sum/div)
        x.append(i)
        sum = 0

    
plt.plot(x, y1)
plt.plot(x, y2)
plt.show()
    
sense.clear()
