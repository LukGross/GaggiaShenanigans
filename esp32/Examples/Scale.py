# Example for Pycom device, gpio mode
# Connections:
# Pin # | HX711
# ------|-----------
# P9    | data_pin
# P10   | clock_pin
#

from hx711 import HX711
from machine import Pin
from time import sleep, ticks_us, ticks_diff

pin_DTL = Pin(19, Pin.IN, pull=Pin.PULL_DOWN)
pin_DTR = Pin(21, Pin.IN, pull=Pin.PULL_DOWN)
pin_SCK = Pin(18, Pin.OUT)

scale = HX711(pin_SCK, pin_DTL, pin_DTR)
sleep(1)
print(scale.OFFSET)
scale.tare()
print(scale.OFFSET)
while True:
    t = ticks_us()
    value = round(scale.get_value(),1)
    t = ticks_diff(ticks_us(),t)/1000
    print(value, t)
    sleep(.1)


    