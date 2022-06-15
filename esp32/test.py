from machine import ADC, Pin
from time import sleep, ticks_ms, ticks_diff
from timing import timer
from pressure import pressure

pin = Pin(32)
press = pressure(pin)
n = 100
ptimer = timer("us")

analog = ADC(pin, atten=ADC.ATTN_11DB)
uvolts = 3_300_000
high = 12
low = -1
last_reading = 0
read_raw = analog.read_uv


while True:
    ptimer.start()
    r = range(n)
    reading = 0
    for i in r:
        reading += read_raw()
    val = ((high-low)*(reading/n - uvolts*0.1)
                                  /(uvolts*0.8) + low)
    ptimer.stop()
    print("Pressure: " + str(round(val,1)) + "bar", "Time: "+ str(ptimer.runtime)+ str(ptimer.scale))
    sleep(0.5)
