from hx711 import HX711
from machine import Pin
from time import sleep
from timing import timer

pin_DTL = Pin(19, Pin.IN, pull=Pin.PULL_DOWN)
pin_DTR = Pin(21, Pin.IN, pull=Pin.PULL_DOWN)
pin_SCK = Pin(18, Pin.OUT)
t = timer("us")

scale = HX711(pin_SCK, pin_DTL, pin_DTR)
scale.tare()
while True:
    t.start()
    value = round(scale.get_value(),1)
    t.stop()
    print("Weight:", str(value)+"g ","runtime:", str(t.runtime) + str(t.scale))
    sleep(0.5)


    