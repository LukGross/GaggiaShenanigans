from machine import ADC, Pin
from time import sleep
pin = Pin(32)
while True:
    adc = ADC(pin, atten = ADC.ATTN_11DB)
    val = adc.read_uv()
    print(val)
    sleep(1)
