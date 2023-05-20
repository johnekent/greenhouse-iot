# module imports
import machine
import network
import ssl
import time
import ubinascii
import json

import time
from time import sleep
from machine import Pin, Timer, I2C
import ntptime
import uasyncio as asyncio

from simple import MQTTClient

from status_display import StatusDisplay
from async_web_server import AsyncWebServer

# be explicit so that it fails if config has it missing
from config import LIGHT_SENSOR_CLASS, TEMP_SENSOR_CLASS, WIFI_SSID, WIFI_PASSWORD, MQTT_CLIENT_KEY, MQTT_CLIENT_CERT, MQTT_BROKER, MQTT_BROKER_CA, SCL_PIN, SDA_PIN, DEVICE_NAME

# MQTT topic constants
MQTT_SENSOR_TOPIC = "greenhouse/metrics"

MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id())

ERROR_CODE_WIFI=1
ERROR_CODE_TIME=2
ERROR_CODE_MQTT=3
ERROR_CODE_SENSOR=5
ERROR_CODE_PUBLISH=7

led_config = [{'name': 'orange', 'pin': 1 },
              {'name': 'blue', 'pin': 2 },
              {'name': 'yellow', 'pin': 4 },
              {'name': 'purple', 'pin': 6 },
              {'name': 'pink', 'pin': 8 },
              {'name': 'green', 'pin': 10 },
              {'name': 'red', 'pin': 12 },
              {'name': 'main', 'pin': 'LED'}]

measure_interval = 30
num_measurements = 30

def write_log(msg, log_type):
    ts = str(time.time())
    fn = f"{log_type}-log-{ts}.log"
    with open(fn, 'w') as log:
      log.write(msg)

def connect_wifi(ssid=WIFI_SSID, password=WIFI_PASSWORD):
    # initialize the Wi-Fi interface
    wlan = network.WLAN(network.STA_IF)

    # activate and connect to the Wi-Fi network:
    wlan.active(True)
    wlan.config(pm = 0xa11140)  # Disable power-save mode
    wlan.connect(ssid, password)
    
    wlan_tries = 0
    wlan_max_tries = 15
    while not wlan.isconnected() and wlan_tries < wlan_max_tries:
        print(f"...waiting for wlan connection {wlan_tries}")
        wlan_tries = wlan_tries + 1
        sleep(0.5)
        
    if not wlan.isconnected() or wlan.status() != 3:
        raise Exception(f"Failed to connect to wifi after {wlan_tries} tries with status {wlan.status()}")

    return wlan

def read_keys_and_certs():
    # function that reads PEM file and return byte array of data
    def read_pem(file):
        with open(file, "r") as input:
            text = input.read().strip()
            split_text = text.split("\n")
            base64_text = "".join(split_text[1:-1])
            return ubinascii.a2b_base64(base64_text)
     
    # read the data in the private key, public certificate, and
    # root CA files
    key = read_pem(MQTT_CLIENT_KEY)
    cert = read_pem(MQTT_CLIENT_CERT)
    ca = read_pem(MQTT_BROKER_CA)
    
    return (key, cert, ca)

def connect_mqtt_client(key, cert, ca):

    # create MQTT client that use TLS/SSL for a secure connection
    mqtt_client = MQTTClient(
        MQTT_CLIENT_ID,
        MQTT_BROKER,
        keepalive=60,
        #port=8883,
        ssl=True,
        ssl_params={
            "key": key,
            "cert": cert,
            "server_hostname": MQTT_BROKER,
            "cert_reqs": ssl.CERT_REQUIRED,
            "cadata": ca,
        },
    )
    
    mqtt_client.connect()
    
    return mqtt_client

def create_sensors():
    # Create I2C object
    i2c = machine.I2C(0, scl=machine.Pin(SCL_PIN), sda=machine.Pin(SDA_PIN))

    print("Got i2c... creating light sensor")
    light_sensor = LIGHT_SENSOR_CLASS(i2c=i2c)
    print("...Light sensor created")
    
    temp_sensor = TEMP_SENSOR_CLASS(i2c=i2c)
    print("...Temp sensor created")
        
    return (light_sensor, temp_sensor)

async def take_measurement():
    last_state = None
    try:        
        status.set_on(['main'])
        
        # light
        light_measure = light_sensor.take_measurement()
        print(f"Light = {light_measure}")
        last_state = "Measured Light"
        
        #temperature
        temp_measure = temp_sensor.take_measurement()
        print(f"Temp = {temp_measure}")
        last_state = "Measured Temperature"
        
        # message
        measures = {'light': light_measure, 'temp': temp_measure}
        message = json.dumps({'source': DEVICE_NAME, 'measures': measures})
        print(f"Message is of length {len(message)}")
        
        # publish
        mtqq_publish_retries = 5
        for i in range(mtqq_publish_retries):
            try:
                mqtt_client.publish(MQTT_SENSOR_TOPIC, message)
            except OSError as oe:
                msg = f"mqtt publish got OSError {oe} with args {oe.args}.  WLAN connected = {wlan.isconnected()}.  Try = {i}"
                print(msg)
                if not wlan.isconnected():
                    write_log(msg, "err-mqtt-publish-wlan")
                if i < mtqq_publish_retries - 1:
                    print("Attempting to close and create a new mqtt_client")
                    #mqtt_client.disconnect()  # this tries to write bytes and fails, so only do socket
                    mqtt_client.sock.close()
                    print(".... disconnected -- socket closed")
                    mqtt_client.connect()
                    print(".... Re-Connected")
                    sleep_for = 0.5
                    print(f"Sleeping for {sleep_for}")
                    sleep(sleep_for)
                    continue
                else:
                    write_log(msg, "err-mqtt-publish")
                    raise OSError(msg)
            break
            
        print(f"Published {message} to topic {MQTT_SENSOR_TOPIC}")
        last_state = "Published Measurement"
        
        status.set_off(['main'])
            
    except Exception as e:
        msg = f"During measurement capture received error {e} of type {type(e)} with last state of {last_state}"
        print(msg)
        write_log(msg, "err-measure")
        status.set_on(['red'])
        raise Exception(msg)

if __name__ == "__main__":
    print("Beginning program")

    print("Establishing infrastructure connectivity")
    try:
        status = StatusDisplay(led_config)
        
        # this block is to prevent socket reuse on startup
        button = Pin(20, Pin.IN, Pin.PULL_DOWN)
        
        if button.value():
            print("Button pressed at startup - skipping steps")
            import sys
            status.set_on(['pink'])
            sys.exit()

        status.all_on()
        sleep(3)
        status.all_off()

        print(f"Connecting to Wi-Fi SSID: {WIFI_SSID}")
        wlan = connect_wifi()
        print(f"Connected to Wi-Fi SSID: {WIFI_SSID}")
        status.set_on(['orange'])
        
        # update the current time on the board using NTP
        ### This seems to be important when running the device without connected to PC/Thonny
        
        print("Setting time")
        time_set = False
        tries = 0
        while not time_set and tries < 3:
            try:
                ntptime.settime()
            except Exception as e:
                print(f"...Retrying to set time after exception {e}")
                sleep(1)
                tries = tries + 1
                
        if not time_set:
            print(f"Failed to set time after {tries} attempts... let's see if that's a problem")
        else:
            print(f"Set time using retries = {tries}")
            status.set_on(['blue'])
        
        print("Reading keys")
        (key, cert, ca) = read_keys_and_certs()
        print("Read keys")
        status.set_on(['yellow'])
    
        print(f"Connecting to MQTT broker: {MQTT_BROKER}")
        mqtt_client = connect_mqtt_client(key, cert, ca)
        print(f"Connected to MQTT broker: {MQTT_BROKER} using client {str(mqtt_client)}")
        status.set_on(['purple'])
        
        print("Creating sensors")
        (light_sensor, temp_sensor) = create_sensors()
        print("Created sensors")
        status.set_on(['pink'])
        
        ### The status LEDs have helped with startup.  now give them a rest to save lifespan.
        
        print("Starting status server")
        ws = AsyncWebServer(temp_sensor=temp_sensor, light_sensor=light_sensor, wlan=wlan, background_task=take_measurement, background_interval_sec=measure_interval, status_display=status)
        
        try:
            print("Starting status server")
            status.set_on(['green'])
            asyncio.run(ws.run_server())
        finally:
            status.set_off(['green'])
            print("The server event loop is finishing")
            asyncio.new_event_loop()
        
    except Exception as e:
        msg = f"Received exception during setup of infrastructure {e}"
        print(msg)
        status.set_on(['red'])
        write_log(msg, "err-infra")
        raise Exception(msg)
    print("Established infrastructure connectivity")

    # set the completion light pattern
    print("The program has completed")
    status.all_off()
    status.set_on(['orange','yellow', 'pink'])
    write_log("Completed cycle", "ok")
     