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
from pressure import pressure

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
press_adc = pressure(press_pin)
temp_sens = tsic(temp_pin, Pin(2,Pin.OUT))

# initiate heater PWM and PID-controller #
brewtemp = 95
steamtemp = 200
heater = PWM(heater_pin, freq=1, duty=0)
pid = PID(.7, 0.1, 30, setpoint=brewtemp, scale='s')
pid.sample_time = 1
pid.output_limits = (0, 50)

# actors #
def valve_on():
    valve_pin(0)
def valve_off():
    valve_pin(1)

def pump_on():
    pump_pin(1)
def pump_off():
    pump_pin(0)
    
def heater_on(duty = 1023):
    heater.duty(duty)
def heater_off():
    heater.duty(0)

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
t0 = ticks_ms()
t = t0
t_last = t0
while True:
    t = ticks_ms()
    if t > t_last+999:
        temperature = temp_sens.ReadTemp_c()
        pressure = press_adc.read(100)
        intensity = pid(temperature)
        heater_on(int(1023*intensity/50))
        print("temp:", temperature, ", pid-out:", intensity, ", time:",
              round(ticks_diff(t,t0)/1000), ", pressure: ",
              round(pressure,2), end = "           \r")
        t_last = t
    if is_brew() and is_steam():
        valve_off()
        pump_on()
        pid.setpoint = steamtemp
    elif is_steam():
        pump_off()
        valve_off()
        pid.setpoint = steamtemp
    elif is_brew():
        valve_on()
        pump_on()
        pid.setpoint = brewtemp
    else:
        pid.setpoint = brewtemp
        pump_off()
        valve_off()

all_off()   

