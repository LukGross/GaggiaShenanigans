from machine import ADC, Pin
from time import sleep, ticks_ms, ticks_diff
from timing import timer
from pressure import pressure

pin = Pin(32)
press = pressure(pin)
n = 10
ptimer = timer("us")
while True:
    ptimer.start()
    val = press.read(n)
    ptimer.stop()
    print("Pressure: " + str(round(val,1)) + "bar", "Time: "+ str(ptimer.runtime)+ str(ptimer.scale))
    sleep(0.5)
