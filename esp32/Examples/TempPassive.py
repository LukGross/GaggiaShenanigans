from machine import Pin
from time import sleep
from tsic import tsic


temp = Pin(33, Pin.IN, Pin.PULL_UP)
sens = tsic(temp)

while True:
    temperature = sens.ReadTemp_c()
    print("Temperature: " + str(temperature)+ "°")
    sleep(1)
