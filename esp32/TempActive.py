from machine import Pin
from time import sleep
from tsic import tsicActive

data = Pin(33, Pin.IN, Pin.PULL_UP)
power = Pin(2, Pin.OUT)
tsic = tsicActive(data, power)

while True:
    t = tsic.ReadTemp_c()
    print(t)
    sleep(0.5)
