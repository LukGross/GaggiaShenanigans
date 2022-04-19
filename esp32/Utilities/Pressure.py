from machine import ADC, Pin
from time import sleep, ticks_ms, ticks_diff

pin = Pin(32)
adc = ADC(pin, atten=ADC.ATTN_11DB)
n = 100
while True:
    t = ticks_ms()
    v = 0
    for i in range(n):
        v = 20.6843*(adc.read_uv() - 330000)/2600000/n
    val = v
    t2 = ticks_ms()
    print("Pressure: " + str(round(val,1)) + "bar", "Time: ", ticks_diff(t2,t), "ms")
    sleep(.5)
