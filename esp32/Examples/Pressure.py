from machine import ADC, Pin
from time import sleep, ticks_ms, ticks_diff
from pressure import pressure

pin = Pin(32)
press = pressure(pin)
n = 10
while True:
    t = ticks_ms()
    val = press.read(n)
    t2 = ticks_ms()
    print("Pressure: " + str(round(val,1)) + "bar", "Time: ", ticks_diff(t2,t), "ms")
    sleep(.5)
