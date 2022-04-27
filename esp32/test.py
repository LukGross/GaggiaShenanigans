from time import sleep_ms, ticks_ms, ticks_diff, ticks_us, sleep, sleep_us
mss = 0
t0 = ticks_ms()
#while ticks_diff(ticks_ms(),t0)<=10_000:
#    mss += 1
print(mss)

c = 0
t = 0
ts = ticks_ms()
while ticks_diff(ticks_ms(),ts) <= 1_000:
    t0 = ticks_us()
    sleep_us(10)
    t += ticks_diff(ticks_us(), t0)
    c += 1
    
print(t/c)
