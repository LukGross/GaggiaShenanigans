from time import ticks_us, ticks_diff

a = 20
dic = {"a":5, "b":3, "c":30}

c = 0
t0 = ticks_us()
for i in range(1000):
    c = a
    
t1 = ticks_us()   
for i in range(1000):
    c = dic["a"]
    
t2 = ticks_us()

print(ticks_diff(t1,t0)/1000, ticks_diff(t2,t1)/1000)