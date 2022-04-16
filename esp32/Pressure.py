from machine import ADC, Pin
from time import sleep

pin = Pin(32)
while True:
    adc = ADC(pin, atten=ADC.ATTN_11DB)
    val = 20.6843*(adc.read_uv() - 330000)/2600000
    print("Pressure: " + str(round(val,1)) + "bar")
    print(adc.read_uv())
    sleep(.5)
