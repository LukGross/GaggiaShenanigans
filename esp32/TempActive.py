from machine import Pin
from time import ticks_cpu, ticks_ms, ticks_us, ticks_diff, sleep, sleep_ms, sleep_us
from array import array



data = Pin(15, Pin.IN)
relais = Pin(5, Pin.OUT)
power = Pin(4, Pin.OUT)
power.value(0)

def ReadBitTime():
    while data.value() == 1:
        pass
    t = ticks_cpu()
    while data.value() == 0:
        pass
    t = ticks_diff(ticks_cpu(),t)
    return t

def ReadZACwire():
    length = 20
    reading = array('I', range(length))
    power.value(1)
    for i in range(length):
        reading[i] = ReadBitTime()
    power.value(0)
    return reading
    
def ReadTemp():
    reading = ReadZACwire()
    byte = 0
    for entry in reading[6:9]:
        if entry > 8000:
            byte = byte << 1 | 0
        else:
            byte = byte << 1 | 1
    for entry in reading[11:19]:
        if entry > 8000:
            byte = byte << 1 | 0
        else:
            byte = byte << 1 | 1
    return byte/2047*200-50
     
N = 10
ReadTemp()
t = ticks_ms()
for i in range(N):
    print(ReadTemp())
t = ticks_diff(ticks_ms(), t)
print(t/N)





    #power.value(1)
    #msb = ReadByte()
    #lsb = ReadByte()
    #reading = (msb << 8) | lsb
    #temperature = (reading * 200.0 / 2047.0) + 50
    #print("Temperature = {}". format(temperature))
    #power.value(0)
    #sleep(.5)