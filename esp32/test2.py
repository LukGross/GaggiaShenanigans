# Example for Pycom device, gpio mode
# Connections:
# Pin # | HX711
# ------|-----------
# P9    | data_pin
# P10   | clock_pin
#

from hx711_gpio import HX711
from machine import Pin
from time import sleep, ticks_us, ticks_diff

pin_OUT = Pin(19, Pin.IN, pull=Pin.PULL_DOWN)
pin_SCK = Pin(18, Pin.OUT)

left = HX711(pin_SCK, pin_OUT, gain = 128)
left.tare()
#right = HX711(pin_SCK, pin_OUT, gain = 128)
#right.tare()
while True:
    t1 = ticks_us()
    value = left.read()
    t2 = ticks_us()
    #value2 = left.read()
    #t3 = ticks_ms()
    t = ticks_diff(t2, t1)
    #t_ = ticks_diff(t3, t2)
    print(t, value)
    sleep(1)


    