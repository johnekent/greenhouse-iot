"""https://github.com/raspberrypilearning/physical-computing-guide/blob/master/pull_up_down.md

E.g. for a fluid float switch
Flip the GPIO to LOW when the switch is on (low water level.)
"""
import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

switch_pin = 27

GPIO.setup(switch_pin, GPIO.IN, GPIO.PUD_UP)

while True:
    button_state = GPIO.input(switch_pin)
    if button_state == GPIO.HIGH:
      print ("HIGH")
    else:
      print ("LOW")
    time.sleep(0.5)
