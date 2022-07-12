import time

import board
import adafruit_dht as adafruit_dht

for i in range(0, 5):
    device = adafruit_dht.DHT22(board.D17, use_pulseio=False)
    #device = adafruit_dht.DHTBase(False, pin=board.D4, trig_wait=5000, use_pulseio=False, max_pulses=90)
    print("Sleeping to get a measurement")
    time.sleep(5)
    try:
        t_c = device.temperature
        t_f = t_c * (9/5) + 32
        h = device.humidity
        print(f"Device DHT22 read {t_c} Celsius which is {t_f} Fahrenheit and humidity {h}")
    except RuntimeError as rte:
        print(f"Uh oh got {rte} for iteration {i}")
