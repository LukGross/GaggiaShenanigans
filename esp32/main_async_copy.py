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

# General Imports #
from timing import timer
import uasyncio as aio

# Pin Declarations #
from machine import Pin
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

# initiat light PWM #
from machine import PWM
light = PWM(light_pin, freq=1, duty = 512)

# read parameters from params.json #
import json
params_file = open("params.json")
params = json.load(params_file)
params_file.close

def save_params():
    params_file = open("params.json", "w")
    json.dump(params, params_file)
    params_file.close()

# initiate tsic, scale and pressure adc #
from tsic_timer import tsic
temp_sens = tsic(temp_pin, Pin(2,Pin.OUT))

from hx711 import HX711
scale = HX711(scl_scale_pin, dt_left_pin, dt_right_pin)

from pressure import pressure
press_adc = pressure(press_pin)

# initiate heater PWM and PID-controller #
heater = PWM(heater_pin, freq=1, duty=0)


from PID_discounted import PID
pid = PID(30, 10, 300, setpoint=params["brewtemp"], scale='s', gammai = .99)
pid.sample_time = 1
pid.output_limits = (0, 1023)

# actors #
def valve_on():
    valve_pin(0)
def valve_off():
    valve_pin(1)
def is_valve():
    return int(not valve_pin())


def pump_on():
    pump_pin(1)
def pump_off():
    pump_pin(0)
def is_pump():
    return pump_pin()
    
def heater_on(duty = 1023):
    if duty == None:
        duty = 0
    else:
        duty = int(duty)
    heater.duty(duty)
def heater_off():
    heater.duty(0)
def heater_duty():
    return heater.duty()

def light_on():
    light.init(freq = 1000, duty = 0)
def light_off():
    light.init(freq = 1000, duty = 1023)
def light_idle():
    light.init(freq = 1, duty = 512)
def light_brewing():
    light.init(freq = 4, duty = 512)                    
def is_light():
    return int(light.duty()  < 1023)
    
def all_off():
    pump_off()
    heater_off()
    valve_off()
    light_off()
    
def sos():
    all_off()
    from time import sleep_ms
    while True:
        for wait in [100,300,100]:
            for i in range(3):
                light_on()
                sleep_ms(wait)
                light_off()
                sleep_ms(wait)
            sleep_ms(200)
        sleep_ms(300)
    
# switches #
class switches:
    def __init__(self, brew_pin, steam_pin):
        self.brew_pin = brew_pin
        self.steam_pin = steam_pin
        self.is_brew = 0
        self.is_steam = 0
        self.was_brew = 0
        self.was_steam = 0
        self.update()
    
    def __call__(self):
        return self.is_brew, self.was_brew, self.is_steam, self.was_steam

    def update(self):
        self.was_brew = self.is_brew
        self.was_steam = self.is_steam
        self.is_brew = self.brew_pin()
        self.is_steam = self.steam_pin()
    
    def unchanged(self):
        self.update()
        return self.was_brew == self.is_brew and self.was_steam == self.is_steam

sw = switches(brew_pin, steam_pin)

# initiate server #
from microdot_asyncio import Microdot
app = Microdot()

@app.route('/get_params')
async def get_params(request):
    global params
    return str(params)

@app.route('/set_params')
async def set_params(request):
    global params
    params["pre_time"] = int(request.args['pre_time'])/10
    params["brew_time"] = int(request.args['brew_time'])/10
    params["pre_pressure"] = int(request.args['pre_pressure'])/10
    params["full_pressure"] = int(request.args['full_pressure'])/10
    params["brewtemp"] = int(request.args['brewtemp'])/10
    params["steamtemp"] = int(request.args['steamtemp'])/10
    save_params()
    return 'params set to ' + str(params)

@app.route('/get_state')
async def get_state(request):
    response = ("temperature: " + str(round(temp_sens.ReadTemp_c(),1)) + "°C; "
                + "pressure: " + str(round(press_adc.read(),1)) + "bar; "
                + "weight: " + str(round(scale.get_value(),1)) + "g; "
                + "heater-duty: " + str(round(heater_duty()/1023*100)) + "%; "
                + "pid-goal: " + str(round(pid.setpoint,0)) + "°C; "
                + "steam-temp: " + str(params["steamtemp"]) + "°C; "
                + "brew/steam: " + str(sw()[0]) + " " + str(sw()[2]) + "; "
                + "light/valve/pump: " + str(is_light()) + " " + str(is_valve()) + " " + str(is_pump()))
    return response

@app.route('/get_last')
async def get_last(request):
    global last_duration
    global last_weight
    return "Brewed " + str(last_weight) + " grams of coffee in " + str(last_duration) + " seconds."


# Events and Globals #
switched = aio.Event()
brewing = aio.Event()
last_duration = 0
last_weight = 0

# Coroutines #
# heating control loop
async def heater_control():
    global params
    while True:
        temperature = temp_sens.ReadTemp_c()
        if temperature == None:
            sos()
        if sw.is_steam:
            pid.set_auto_mode(False)
            if temperature < params["steamtemp"]:
                heater_on()
            else:
                heater_off()
            if not brewing.is_set():
                if temperature > params["steamtemp"] - 5:
                    light_off()
                else:
                    light_on()
        else:
            pid.set_auto_mode(True)
            pid.setpoint = params["brewtemp"]
            if not brewing.is_set():    
                if temperature > params["brewtemp"] - 1 and temperature < params["brewtemp"] +1:
                    light_off()
                else:
                    light_on()
            heater_on(pid(temperature))
        await aio.sleep(1)

# brew control loop for standard controls
async def dumb_brew():
    global params
    full_pressure = params["full_pressure"]
    while True:
        if sw.is_brew:
            if not sw.is_steam:
                valve_on()
            else:
                valve_off()
            if press_adc.read() < full_pressure:
                pump_on()
            else:
                pump_off()
        else:
            pump_off()
            valve_off()
        await aio.sleep(0)


#brew control for a weighed or timed brew
async def weigh_brew():
    global params
    global last_duration
    global last_weight
    await aio.create_task(scale.tare_async())
    target_weight = params["target_weight"]
    pre_pressure = params["pre_pressure"]
    full_pressure = params["full_pressure"]
    pre_time = params["pre_time"]*1000
    brew_time = params["brew_time"]*1000
    light_brewing()
    brew_timer = timer()
    brew_timer.start()
    valve_on()
    while sw.brew_pin() and brew_timer.current() < pre_time:
        if press_adc.read() < pre_pressure:
            pump_on()
        else:
            pump_off()
        await aio.sleep(0)
    while sw.brew_pin() and (scale.get_value() < target_weight and brew_timer.current() < brew_time):
        if press_adc.read() < full_pressure:
            pump_on()
        else:
            pump_off()
        await aio.sleep(0)
    pump_off()
    valve_off()
    light_idle()
    last_duration = round(brew_timer.stop()/1000,1)
    last_weight = round(scale.get_value(),1)

# hot water functionality
async def hot_water():
    valve_off()
    pump_on()
    while sw.brew_pin():
        await aio.sleep_ms(10)
    pump_off()

# flushing after brew
async def flush():
    wait_time = 600000
    flush_time = 4000
    flush_timer = timer()
    flush_timer.start()
    while sw.brew_pin() and flush_timer.current() < wait_time:
        await aio.sleep_ms(10)
    while not sw.brew_pin() and flush_timer.current() < wait_time:
        await aio.sleep_ms(10)
    if flush_timer.current() < wait_time:
        flush_timer.start()
        valve_on()
        pump_on()
        while sw.brew_pin() and flush_timer.current() < flush_time:
            await aio.sleep_ms(10)
    pump_off()
    valve_off()
    light_on()
        
# repl loop
async def repl(debug = False):
    while True:
        if debug:
            print("temperature: " + str(round(temp_sens.ReadTemp_c(),1)) + "°C; "
                  + "pressure: " + str(round(press_adc.read(),1)) + "bar; "
                  + "weight: " + str(round(scale.get_value(),1)) + "g; "
                  + "heater-duty: " + str(round(heater_duty()/1023*100)) + "%; "
                  + "pid-goal: " + str(round(pid.setpoint,0)) + "°C; "
                  + "steam-temp: " + str(params["steamtemp"]) + "°C; "
                  + "brew/steam: " + str(sw()[0]), str(sw()[2]) + "; "
                  + "light/valve/pump: " + str(is_light()), str(is_valve()), str(is_pump())
                  , end = "           \r")
        else:
            print("temperature: " + str(temp_sens.ReadTemp_c()) + "°; "
                  + "pressure: " + str(round(press_adc.read(),1)) + "bar; "
                  + "weight: " + str(round(scale.get_value(),1)) + "g"
                  , end = "           \r")
        await aio.sleep(.5)
        
# logging loop
async def sensor_logging(debug = False):
    log_path = "logging/log.txt"
    log = open(log_path, "w")
    while True:
        if debug:
            log.write("temperature: " + str(round(temp_sens.ReadTemp_c(),1)) + "°C; "
                      + "pressure: " + str(round(press_adc.read(),1)) + "bar; "
                      + "weight: " + str(round(scale.get_value(),1)) + "g; "
                      + "heater-duty: " + str(round(heater_duty()/1023*100)) + "%; "
                      + "pid-goal: " + str(round(pid.setpoint,0)) + "°C; "
                      + "steam-temp: " + str(params["steamtemp"]) + "°C; "
                      + "brew/steam: " + str(sw()[0]) + str(sw()[2]) + "; "
                      + "light/valve/pump: " + str(is_light()) + str(is_valve()) + str(is_pump()) + "\n")
        else:
            log.write(str(temp_sens.ReadTemp_c()) + "," + str(press_adc.read()) + "," + str(scale.get_value()) + "\n")
        await aio.sleep(.5)

# switch watcher
async def switch_watcher():
    while sw.unchanged():
        await aio.sleep(.01)
    switched.set()

async def switch_watcher_dumb():
    while True:
        sw.update()
        await aio.sleep(.01)

# main routines #
# pid heating + standard gaggia classic brewing
async def main_dumb():
    loop = aio.get_event_loop()
    heater_task = aio.create_task(heater_control())
    brew_task = aio.create_task(dumb_brew())
    server_task = aio.create_task(app.start_server(port = 80))
    #repl_task = aio.create_task(repl())
    #logging_task = aio.create_task(sensor_logging())
    switches_task = aio.create_task(switch_watcher_dumb())
    loop.run_forever()

# pid heating + smart brewing
async def main():
    heater_task = aio.create_task(heater_control())
    server_task = aio.create_task(app.start_server(port = 80))
    #repl_task = aio.create_task(repl())
    #logging_task = aio.create_task(sensor_logging())
    while True:
        switched.clear()
        if sw.is_brew and not sw.is_steam:
            app.shutdown()
            brewing.set()
            brew_task = aio.create_task(weigh_brew())
            await brew_task
            flush_task = aio.create_task(flush())
            await flush_task
            brewing.clear()
        if sw.is_brew and sw.is_steam:
            app.shutdown()
            switches_task = aio.create_task(switch_watcher())
            hot_task = aio.create_task(hot_water())
            await switches_task
            await hot_task
        else:
            server_task = aio.create_task(app.start_server(port = 80))
            switches_task = await aio.create_task(switch_watcher())
            
            

if sw.is_steam:
    aio.run(main_dumb())
    pass
else:
    aio.run(main())
    pass
sos()


