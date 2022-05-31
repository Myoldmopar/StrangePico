import machine
import neopixel

np = neopixel.NeoPixel(machine.Pin(4), 144)
for x in range(144):
    np[x] = (0, 0, 0)
np.write()
