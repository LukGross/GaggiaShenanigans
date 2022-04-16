from machine import Pin, PWM, ADC
from time import sleep, ticks_us, ticks_ms
from tsic import tsic


temp = Pin(33, Pin.IN, Pin.PULL_UP)
#press = ADC(Pin(15), atten=ADC.ATTN_11DB)
#pump = Pin(18, Pin.IN, Pin.PULL_DOWN)
#steam = Pin(19, Pin.IN, Pin.PULL_DOWN)
#relais = Pin(21, Pin.OUT)
#led = Pin(5, Pin.OPEN_DRAIN)
#led.value(0)
ttemp = ticks_ms()
sens = tsic(temp)
while True:
    temperature = sens.ReadTemp_c()
    #pressure = (round(20.6843*(press.read_uv() - 330000)/2600000,1))
    #led.value(not steam.value())
    #relais.value(pump.value())
    print(temperature)
    sleep(.5)
