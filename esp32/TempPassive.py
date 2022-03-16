from machine import Pin
from time import sleep, ticks_us
from tsic import tsic306
    

temp = Pin(15, Pin.IN, Pin.PULL_UP)
led = Pin(2, Pin.OUT)

tsic = tsic306(temp)

sleep(1)
while True:
    t = tsic.ReadTemp_int()
    print(t)
    if t == None:
        led.value(0)
    else:
        if t > 25:
            led.value(1)
        else:
            led.value(0)
    sleep(.1)