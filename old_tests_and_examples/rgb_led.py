from machine import Pin
from time import sleep


p_red = Pin(15, Pin.OUT)
p_red.high()
p_green = Pin(14, Pin.OUT)
p_green.high()
p_blue = Pin(13, Pin.OUT)
p_blue.high()

p_blue.low()
#p_green.low()
#p_red.low()

# while True:
#     for p in [p_red, p_green, p_blue]:
#         p.low()
#         sleep(0.25)
#         p.high()
# 
#     for s in [(p_red, p_green), (p_red, p_blue), (p_green, p_blue)]:
#         s[0].low()
#         s[1].low()
#         sleep(0.25)
#         s[0].high()
#         s[1].high()
# 