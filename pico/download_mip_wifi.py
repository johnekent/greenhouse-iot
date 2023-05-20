#https://www.hackster.io/sandeep-mistry/connect-your-raspberry-pi-pico-w-to-aws-iot-core-8868b7
import network
import mip
import time

# update with your Wi-Fi network's configuration
WIFI_SSID = "Kent-Eero"
WIFI_PASSWORD = "pink90bells863more"

wlan = network.WLAN(network.STA_IF)

print(f"Connecting to Wi-Fi SSID: {WIFI_SSID}")

wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASSWORD)

while not wlan.isconnected():
    time.sleep(0.5)

print(f"Connected to Wi-Fi SSID: {WIFI_SSID}")

mip.install("https://raw.githubusercontent.com/micropython/micropython-lib/master/micropython/umqtt.simple/umqtt/simple.py")