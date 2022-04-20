from machine import Pin
from time import sleep, ticks_ms, ticks_diff
from tsic import tsicActive

data = Pin(33, Pin.IN, Pin.PULL_UP)
power = Pin(2, Pin.OUT)
tsic = tsicActive(data, power)
t0 = ticks_ms()
while True:
    t = tsic.ReadTemp_c()
    print(t, ticks_diff(ticks_ms(), t0))
