"""
status_display.py

Manage the display of status commands
"""
from machine import Pin
from time import sleep

class StatusDisplay:
    """
    initialization and methods for controlling leds and managing their display
    """
    leds = {}
    
    def __init__(self, config):
        """
        Config is a list of {'name': 'the reference name', 'pin': 'the gpio pin number as an int'}
        """
        error_count = 0
        for item in config:
            print(item)
            try:
                led = Pin(item['pin'], Pin.OUT)
                led.on()
            except Exception as e:
                print(f"Skipping config item {item} due to error {e}")
                error_count = error_count + 1
            
            self.leds[item['name']] = led
            
        self.all_off()
            
        print(f"The indicators of names {self.leds.keys()} are available with {error_count} errors encountered.")
    
    def all_on(self):
        self.set_on(self.leds.keys())
            
    def all_off(self):
        self.set_off(self.leds.keys())
            
    def set_on(self, names):
        for name in names:
            self.leds[name].on()

    def set_off(self, names):
        for name in names:
            self.leds[name].off()

if __name__ == "__main__":
    print("in main")
    # ability to test without "deploying" to device
    led_config = [{'name': 'orange', 'pin': 1 },
                  {'name': 'blue', 'pin': 2 },
                  {'name': 'yellow', 'pin': 4 },
                  {'name': 'purple', 'pin': 6 },
                  {'name': 'pink', 'pin': 8 },
                  {'name': 'green', 'pin': 10 },
                  {'name': 'red', 'pin': 12 },
                  {'name': 'main', 'pin': 'LED'}]
    
    sd = StatusDisplay(led_config)
    sd.all_on()
    sleep(5)
    sd.all_off()
    
    sd.set_on(['orange','yellow','pink', 'red'])
    sleep(2)
    sd.set_on(['blue','purple','green', 'main'])
    sleep(2)
    sd.set_off(['orange','yellow','pink', 'red'])
    sleep(2)
    sd.set_off(['blue','purple','green', 'main'])
    
    for item in led_config:
        sd.set_on([item['name']])
        sleep(1)
        
    sd.all_off()

