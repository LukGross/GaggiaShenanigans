from machine import Pin
from time import sleep
from tsic import tsicActive


data = Pin(33, Pin.IN, Pin.PULL_UP)
power = Pin(2, Pin.OUT)
sens = tsicActive(data, power)

while True:
    temperature = sens.ReadTemp_c()
    print("Temperature: " + str(temperature)+ "°")
    sleep(1)
