from machine import Pin
from time import sleep, ticks_us
from tsic import tsic306
    

def function(a):
    if a > 2:
        return a
    a = a + 1
    print("whoop")
    return a