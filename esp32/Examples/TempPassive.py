from machine import Pin
from time import sleep
from tsic import tsic
from timing import timer

temp = Pin(33, Pin.IN, Pin.PULL_UP)
sens = tsic(temp)
temptimer = timer("us")

while True:
    temptimer.start()
    temperature = sens.ReadTemp_c()
    temptimer.stop()
    print("Temperature: " + str(temperature)+ "° ", "Runtime: " +str(temptimer.runtime)+temptimer.scale)
    sleep(.1)
