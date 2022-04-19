# Gaggia Final Build
# Connections:
# Pin   | function
# ------|-----------
#       | OUTs:
# 4     | solenoid valve ssr
# 5     | pump ssr
# 15    | heater ssr
# 14    | heating light (open drain)
# 18    | scl scale
#       | INs:
# 13    | steam switch
# 12    | brew switch
# 19    | dt scale left
# 21    | dt scale right
# 33    | temperature probe
# 32    | pressure transducer


# Imports #
from machine import Pin, ADC, PWM
from time import sleep, ticks_us, ticks_ms, ticks_diff, time
from tsic import tsic
from PID import PID
from random import randint

# Pin Declarations #
# OUT
valve_pin = Pin(4, Pin.OUT, value = 1)
pump_pin = Pin(5, Pin.OUT, value = 0)
heater_pin = Pin(15, Pin.OUT, value = 0)
scl_scale_pin = Pin(18, Pin.OUT, value = 0)
light_pin = Pin(14, Pin.OPEN_DRAIN, value = 1)
# IN
dt_left_pin = Pin(19, Pin.IN, Pin.PULL_DOWN)
dt_right_pin = Pin(21, Pin.IN, Pin.PULL_DOWN)
steam_pin = Pin(13, Pin.IN, Pin.PULL_DOWN)
brew_pin = Pin(12, Pin.IN, Pin.PULL_DOWN)
temp_pin = Pin(33, Pin.IN, Pin.PULL_UP)
press_pin = Pin(32, Pin.IN)

# initiate tsic, scale and pressure adc #
press_adc = ADC(press_pin, atten=ADC.ATTN_11DB)
temp_sens = tsic(temp_pin)

# actors #
def valve_on():
    valve_pin(0)
def valve_off():
    valve_pin(1)

def pump_on():
    pump_pin(1)
def pump_off():
    pump_pin(0)
    
def heater_on():
    heater_pin(1)
def heater_off():
    heater_pin(0)

def light_on():
    light_pin(0)
def light_off():
    light_pin(1)
    
def all_off():
    pump_off()
    heater_off()
    valve_off()
    light_off()
    
# switches #
def is_steam():
    return steam_pin()

def is_brew():
    return brew_pin()


# Program #
pid = PID(1, 0.1, 30, setpoint=35, scale='s')
pid.sample_time = 1
pid.output_limits = (0, 50)
pwm = PWM(heater_pin, freq=1, duty=0)
intensity = 0
file = open("test.csv", "w")
cond = True
t0 = time()
t = t0
t_last = t0
sleep(1)
pressure = 0
while t-t0 < 200:
    t = time()
    if t > t_last:
        temperature = temp_sens.ReadTemp_c()
        intensity = pid(temperature)
        pwm.duty(int(1023*intensity/50))
        file.write(str(t) + "," + str(intensity) + ","
                   + str(temperature) + "\n")
        print("temp: ", temperature, "pid-out: ", intensity, "time: ", t-t0, "pressure: ", pressure, end = "           \r")
    
    if is_brew():
        light_on()
        valve_on()
        p = 0
        for j in range(100):
            p += 20.6843*(press_adc.read_uv() - 330000)/2600000/100
        pressure = p
        if pressure < 9:
            pump_on()
        else:
            pump_off()

    else:
        light_off()
        pump_off()
        valve_off()
    
    t_last = t

#all_off()
pwm.duty(0)    
file.close()
