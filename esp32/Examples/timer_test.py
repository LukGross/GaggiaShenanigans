from timing import timer
from time import ticks_cpu, ticks_diff, sleep, ticks_us
tim = timer("us")

def do():
    start_ = tim.start
    stop_ = tim.stop
    start = 0
    stop = 0
    for i in range(20):
        t0 = ticks_us()
        start_()
        stop_()
        t1 = ticks_us()
        start = ticks_us()
        stop = ticks_diff(ticks_us(), start)
        t2 = ticks_us()
        print("timer:", tim.runtime, "ticks:", stop, "difference:", ticks_diff(t1,t0)-ticks_diff(t2,t1) )
do()
