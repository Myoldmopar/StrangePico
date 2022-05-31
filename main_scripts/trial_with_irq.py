from time import sleep
from math import pi, sin
from machine import Pin, Timer
from neopixel import NeoPixel


"""
This manages my Doctor Strange costume LEDs based on button press events.
Main bus:
 - Port 36, which is 3.3v, is wired to the main + bus on the breadboard
 - Port 38, which is ground, is wired to the main - bus on the breadboard
Input buttons:
 - All buttons are wired from the IO pins to the main + bus, so that events can be caught upon rising situations
 - Charge button is connected to GP16
 - Moral button is connected to GP19
 - Cancel button is connected to GP22
Outputs:
 - 144 pixel Neopixel strip connected with red to the main + bus, white to the main - bus, and green to GP28
"""


class StrangePixel:
    """A class representing a single RGB pixel along an LED strip, with RGB members along with x and index members"""
    
    def __init__(self, index: int, x: float):
        """
        Initialize the StripRGBPixel instance.

        :param index: Zero-based index of pixel on the LED strip
        :param x: A physical representation of the x-position of this pixel, not necessarily accurate to real-life
        """
        self.index = index
        self.x = x
        self.intensity = 0
        self.red = 0
        self.green = 0
        self.blue = 0

    def set_pixel_intensity(self, intensity: int, evil: bool) -> None:
        """
        Updates the pixel based on an intensity.  RGB values are updated according to good/evil status.
        
        :param intensity: Intensity should be an integer from 0 to 255
        :param evil: A boolean flag specifying whether the pixel color should indicate evil for True, or good for False
        """
        self.intensity = intensity
        if not evil:
            self.red = 0
            self.green = int(intensity)
            self.blue = 0
        else:
            self.red = int(intensity)
            self.green = 0
            self.blue = int(intensity)


class StateManager:
    """Handles all raw I/O with the buttons on the board, converting signals into flags, and handling debounce"""
    
    Idle = 0  # no lights on, waiting on input
    Charging = 1  # arms charging up in the correct color scheme, accents glowing
    Armed = 2  # accents bright, charging paths on but dim, wrists and hands glowing bright
    Calming = 3  # all lights calmly turn off
    
    def __init__(self):
        self.charge_requested = False    
        self.toggle_good_evil_requested = False
        self.abort_requested = False
        self.timer = Timer()
        self._initialize_button_monitors()
        self.evil = False
        self.debounce_time = 200  # ms
        
    def _initialize_button_monitors(self) -> None:
        """One-time initialization to create button instances and call the workers to set up IRQ monitors"""
        self.charge_button = Pin(16, Pin.IN)
        self.initialize_charge_button()
        self.good_evil_button = Pin(19, Pin.IN, Pin.PULL_DOWN)
        self.initialize_good_evil_button()
        self.off_button = Pin(22, Pin.IN, Pin.PULL_DOWN)
        self.initialize_off_button()

    def initialize_charge_button(self, _: Timer=None) -> None:
        """Resets the IRQ monitoring of the charge button"""
        self.charge_button.irq(handler=self.handler_charge, trigger=Pin.IRQ_RISING)

    def handler_charge(self, _):
        """Handles charge button event, turns off monitor for debounce, sets the flag, and schedules an IRQ reset"""
        print("In handler charge")
        self.charge_button.irq(handler=None)
        self.charge_requested = True
        self.timer.init(mode=Timer.ONE_SHOT, period=self.debounce_time, callback=self.initialize_charge_button)

    def initialize_good_evil_button(self, _: Timer=None) -> None:
        """Resets the IRQ monitoring of the moral button"""
        self.good_evil_button.irq(handler=self.handler_trigger_good_evil, trigger=Pin.IRQ_RISING)

    def handler_trigger_good_evil(self, _):
        """Handles moral button event, turns off monitor for debounce, sets the flag, and schedules an IRQ reset"""
        print("In moral button")
        self.good_evil_button.irq(handler=None)
        self.toggle_good_evil_requested = True
        self.timer.init(mode=Timer.ONE_SHOT, period=self.debounce_time, callback=self.initialize_good_evil_button)

    def initialize_off_button(self, _: Timer=None) -> None:
        """Resets the IRQ monitoring of the abort button"""
        self.off_button.irq(handler=self.handler_should_abort, trigger=Pin.IRQ_RISING)

    def handler_should_abort(self, _):
        """Handles abort button event, turns off monitor for debounce, sets the flag, and schedules an IRQ reset"""
        print("In abort button")
        self.off_button.irq(handler=None)
        self.abort_requested = True
        self.timer.init(mode=Timer.ONE_SHOT, period=self.debounce_time, callback=self.initialize_off_button)
        

class DoctorStrangeCostume:
    """Main costume driver, handles all costume output, holds an instance of a StateManager for interacting with IO"""
    
    def __init__(self):
        self.num_leds = 144
        self.strip = NeoPixel(Pin(28), self.num_leds)
        self.num_charging_waves = 3  # number of oscillations during charging
        initial_offset = -pi / 2.0  # setting this as a quarter period makes it charge up nicely
        self.lights_per_period = self.num_leds / self.num_charging_waves
        self.pixels = []
        for i in range(0, self.num_leds):
            x = i * (2 * pi / self.lights_per_period) + initial_offset
            p = StrangePixel(i, x)
            self.pixels.append(p)
        self.state_manager = StateManager()
       
    def refresh_and_check_state(self) -> bool:
        """Checks all state flags, keep in mind it should generally just set up signals for the main_loop to respond"""
        if self.state_manager.abort_requested:
            self.turn_off()
            self.state_manager.abort_requested = False
            self.state_manager.charge_requested = False
            return False
        if self.state_manager.toggle_good_evil_requested:
            self.state_manager.evil = not self.state_manager.evil
            for p in self.pixels:
                p.set_pixel_intensity(p.intensity, self.state_manager.evil)
            self.update()
            self.state_manager.toggle_good_evil_requested = False
        if self.state_manager.charge_requested:
            self.state_manager.abort_requested = False  # dismiss any past abort requests
        return True

    def run_main_loop(self) -> None:
        """Runs infinitely, operating the costume based on all flags.  State is checked often to handle events"""
        while True:
            print(f"In main loop: charge = {self.state_manager.charge_requested}, moral = {self.state_manager.toggle_good_evil_requested}, abort = {self.state_manager.abort_requested}")
            should_restart_main_loop = False
            if self.state_manager.charge_requested:
                self.state_manager.charge_requested = False  # and go ahead and run, but reset the flag for this request
            else:
                sleep(0.2)
                continue
            
            try:
                num_times_to_charge = 2  # number of times to charge before fading and resonating
                target_value = 15  # final target value for arm while resonating wrist
                num_steps = 20  # number of steps to fade to target value
                max_val = 255  # maximum brightness during charge-up
                amplitude = max_val / 2.0

                # charge up the arm
                for iteration in range(0, self.num_leds * num_times_to_charge):
                    if not self.refresh_and_check_state():
                        should_restart_main_loop = True
                        break
                    # each iteration, we just want to walk from the end to the beginning, and
                    # move the value from upstream down one, then calculate a new value for the zeroth element by
                    # adding a small shift to the calculated value
                    for i in range(self.num_leds - 1, 0, -1):
                        self.pixels[i].set_pixel_intensity(self.pixels[i - 1].intensity, self.state_manager.evil)
                    this_shift = iteration * 2 * pi * self.num_charging_waves / self.num_leds
                    self.pixels[0].set_pixel_intensity(
                        int(amplitude + amplitude * sin(self.pixels[0].x - this_shift)),
                        self.state_manager.evil
                    )
                    self.update()

                # restart main loop if we should abort
                if should_restart_main_loop:
                    continue

                # fade down to the target value
                # store the values before we start altering them
                step_sizes = []
                for i in range(0, self.num_leds):
                    actual_distance = target_value - self.pixels[i].intensity  # positive if we are too low
                    step_sizes.append(actual_distance / num_steps)

                # now actually go in and gradually get them close to the target value (round-off error will occur)
                for step in range(0, num_steps):
                    if not self.refresh_and_check_state():
                        should_restart_main_loop = True
                        break
                    for i in range(0, self.num_leds):
                        new_intensity = int(self.pixels[i].intensity + step_sizes[i])
                        if new_intensity < 0:
                            new_intensity = 0
                        self.pixels[i].set_pixel_intensity(new_intensity, self.state_manager.evil)
                    self.update()

                # restart main loop if we should abort
                if should_restart_main_loop:
                    continue
                
                # now one final pass to get them all to the target value
                for i in range(0, self.num_leds):
                    self.pixels[i].set_pixel_intensity(target_value, self.state_manager.evil)
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
                    if not self.refresh_and_check_state(): # no need to set should_restart_main_loop, we are at the end
                        break
                    for val in resonating_values:
                        for i in range(starting_point_for_resonating, self.num_leds):
                            self.pixels[i].set_pixel_intensity(val, self.state_manager.evil)
                        self.update()
                
                # don't allow charge requests while running
                self.state_manager.charge_requested = False
                
            except Exception as e:
                print(f"EXCEPTION: {str(e)}")

    def turn_off(self) -> None:
        """Turns off the LED strip and clears flags"""
        for i in range(0, self.num_leds):
            self.pixels[i].set_pixel_intensity(0, self.state_manager.evil)
        self.update()
        self.state_manager.abort_requested = False

    def update(self) -> None:
        """Updates all LED status based on most recent intensity settings"""
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


if __name__ == "__main__":
    DoctorStrangeCostume().run_main_loop()
