from machine import Pin, Timer
from time import sleep
from _thread import start_new_thread
    

class StoplightOperator:
    """Stoplight class, monitors a button to indicate a car arriving, runs LEDs on a background thread"""

    def __init__(self):
        """Constructor, initializes car_waiting flag and calls to set up LED indicators"""
        self.car_waiting = False
        self.setup_leds()
        
    def setup_leds(self) -> None:
        """Sets up LED indicators"""
        self.green = Pin(15, Pin.OUT)
        self.green.low()
        self.yellow = Pin(14, Pin.OUT)
        self.yellow.low()
        self.red = Pin(13, Pin.OUT)
        self.red.low()
        self.car_led = Pin(25, Pin.OUT)
        self.car_led.low()

    def run_stoplight_loop(self) -> None:
        """Runs an infinite loop, operating the stoplight based on the car_waiting variable"""
        while True:
            self.red.high()
            if self.car_waiting:
                sleep(2)
                self.car_waiting = False
                self.red.low()
                self.green.high()
                sleep(2)
                self.green.low()
                self.yellow.high()
                sleep(1.5)
                self.yellow.low()
                self.red.high()
            sleep(3)

    def initialize_car_monitor(self, timer: Timer=None) -> None:
        """Initializes the car_button variable and sets an IRQ handler to watch for button press event"""
        self.car_button = Pin(16, Pin.IN, Pin.PULL_DOWN)
        self.car_button.irq(handler=self.handle_car_arriving, trigger=Pin.IRQ_RISING)

    def handle_car_arriving(self, pin: Pin) -> None:
        """Handles the button press event, toggling the car_waiting flag, and temporarily disabling IRQ for debounce"""
        self.car_button.irq(handler=None)
        self.set_car_waiting_flag()
        self.timer = Timer()
        self.timer.init(mode=Timer.ONE_SHOT, period=100, callback=self.initialize_car_monitor)

    def set_car_waiting_flag(self) -> None:
        """Small callback for IRQ handler, just to set the car_waiting flag"""
        self.car_waiting = True

    def run_system(self) -> None:
        """Main entry point, starts a thread for the stoplight, starts the car monitor, updates the board LED for waiting indicator"""
        start_new_thread(self.run_stoplight_loop, ())
        self.initialize_car_monitor()
        while True:
            self.car_led.value(self.car_waiting)
            sleep(0.1)


if __name__ == "__main__":
    StoplightOperator().run_system()
