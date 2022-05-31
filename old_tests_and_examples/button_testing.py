from machine import Pin
from time import sleep

led_g = Pin(16, Pin.OUT)
led_f = Pin(13, Pin.OUT)
led_a = Pin(14, Pin.OUT)
led_b = Pin(15, Pin.OUT)

while True:
  led_g.toggle()
  sleep(0.5)
#   led_g.toggle()
#   sleep(0.5)
#   led_f.toggle()
#   sleep(0.5)
#   led_f.toggle()
#   sleep(0.5)
#   led_a.toggle()
#   sleep(0.5)
#   led_a.toggle()
#   sleep(0.5)
#   led_b.toggle()
#   sleep(0.5)
#   led_b.toggle()
#   