import time
import math
from machine import Pin
from neopixel import NeoPixel


class CostumeState:
    # there are different states for what the costume is 'doing'
    Idle = 0  # no lights on, waiting on input
    Charging = 1  # arms charging up in the correct color scheme, accents glowing
    Armed = 2  # accents bright, charging paths on but dim, wrists and hands glowing bright
    Calming = 3  # all lights calmly turn off

    Good = 0  # in this case the target color is green, 0, 255, 0
    Evil = 1  # in this case the target color is red, 255, 0, 0
    

good_evil_status = CostumeState.Good


class PixelyColor:
    Off = (0, 0, 0)
    Red = (255, 0, 0)
    Green = (0, 255, 0)
    Blue = (0, 0, 255)
    White = (255, 255, 255)
    Orange = (219, 87, 0)


class StrangePixel:
    """
    A class representing a single RGB pixel along an LED strip, with RGB members along with x and index members
    """
    def __init__(self, index: int, x: float):
        """
        Initialize the StripRGBPixel instance

        :param index: Zero-based index of pixel on the LED strip
        :param x: A physical representation of the x-position of this pixel, not necessarily accurate to real-life
        """
        self.index = index
        self.x = x
        self.intensity = 0
        self.red = 0
        self.green = 0
        self.blue = 0

    def set_pixel_intensity(self, intensity: int) -> None:
        """
        Updates the pixel based on an intensity.  RGB values are updated according to good/evil status.
        
        :param intensity: Intensity should be an integer from 0 to 255
        """
        global good_evil_status
        self.intensity = intensity
        if good_evil_status == CostumeState.Good:
            self.red = 0
            self.green = int(intensity)
            self.blue = 0
        else:
            self.red = int(intensity)
            self.green = 0
            self.blue = int(intensity)


class ArmLedStrip:
    def __init__(self, gpio_pin_number: int):
        self.num_leds = 144
        self.strip = NeoPixel(Pin(gpio_pin_number), self.num_leds)
        self.num_charging_waves = 3  # number of oscillations during charging
        initial_offset = -math.pi / 2.0  # setting this as a quarter period makes it charge up nicely
        self.lights_per_period = self.num_leds / self.num_charging_waves
        self.pixels = []
        for i in range(0, self.num_leds):
            x = i * (2 * math.pi / self.lights_per_period) + initial_offset
            p = StrangePixel(i, x)
            self.pixels.append(p)

    # def calm(self):
    #     original_led_intensities = []

    def toggle_good_evil(self):
        global good_evil_status
        good_evil_status = CostumeState.Good if good_evil_status == CostumeState.Evil else CostumeState.Evil
        for p in self.pixels:
            p.set_pixel_intensity(p.intensity)
        self.update()

    def charge(self):
        num_times_to_charge = 2  # number of times to charge before fading and resonating
        target_value = 15  # final target value for arm while resonating wrist
        num_steps = 20  # number of steps to fade to target value
        max_val = 255  # maximum brightness during charge-up
        amplitude = max_val / 2.0

        # charge up the arm
        for iteration in range(0, self.num_leds * num_times_to_charge):
            # each iteration, we just want to walk from the end to the beginning, and
            # move the value from upstream down one, then calculate a new value for the zeroth element by
            # adding a small shift to the calculated value
            for i in range(self.num_leds - 1, 0, -1):
                self.pixels[i].set_pixel_intensity(self.pixels[i - 1].intensity)
            this_shift = iteration * 2 * math.pi * self.num_charging_waves / self.num_leds
            self.pixels[0].set_pixel_intensity(
                int(amplitude + amplitude * math.sin(self.pixels[0].x - this_shift))
            )
            self.update()

        # fade down to the target value
        # store the values before we start altering them
        step_sizes = []
        for i in range(0, self.num_leds):
            actual_distance = target_value - self.pixels[i].intensity  # positive if we are too low
            step_sizes.append(actual_distance / num_steps)

        # now actually go in and gradually get them close to the target value (round-off error will occur)
        for step in range(0, num_steps):
            for i in range(0, self.num_leds):
                new_intensity = int(self.pixels[i].intensity + step_sizes[i])
                if new_intensity < 0:
                    new_intensity = 0
                self.pixels[i].set_pixel_intensity(new_intensity)
            self.update()

        # now one final pass to get them all to the target value
        for i in range(0, self.num_leds):
            self.pixels[i].set_pixel_intensity(target_value)
        self.update()

        # then resonate the last half period
        periods_ignored = self.num_charging_waves - 1
        starting_led_of_last_period = self.lights_per_period * periods_ignored + 1
        starting_point_for_resonating = int(starting_led_of_last_period)
        resonating_value_modifiers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                                      19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        # list(range(21)) + list(reversed(range(1, 20)))
        resonating_values = [target_value + x for x in resonating_value_modifiers]
        for _ in range(5):
            for val in resonating_values:
                for i in range(starting_point_for_resonating, self.num_leds):
                    self.pixels[i].set_pixel_intensity(val)
                self.update()
                # time.sleep(0.02)
        # this should be in a try...except block with a KeyboardInterrupt handler that cleans up and returns

    def transition_to(new_color, steps):
        pass

    def turn_off(self):
        for i in range(0, self.num_leds):
            self.pixels[i].set_pixel_intensity(0)
        self.update()

    def update(self):
        for i, p in enumerate(self.pixels):
            r = int(p.red)
            g = int(p.green)
            b = int(p.blue)
            try:
                self.strip[i] = (r, g, b)
            except OverflowError:
                print(f"Red: {r}, Green: {g}, Blue: {b}")
                raise
        self.strip.write()


class DoctorStrangeCostume:

    def __init__(self):
        arm_led_pin = 28
        self.arms = ArmLedStrip(arm_led_pin)  # for now both arms are parallel, ideally we do them individually L/R

    def name(self) -> str:
        return "Doctor Strange Full Costume"

    def run(self):
        print("Waiting for button press ...")
        charge_button = Pin(16, Pin.IN)
        good_evil_button = Pin(19, Pin.IN)
        off_button = Pin(22, Pin.IN)
        while True:
            if charge_button.value():
                self.arms.charge()
            elif good_evil_button.value():
                self.arms.toggle_good_evil()
                time.sleep(0.5)
            elif off_button.value():
                self.arms.turn_off()


if __name__ == "__main__":
    d = DoctorStrangeCostume()
    d.run()


