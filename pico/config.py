"""
Configurations related to the sensor
"""
import adps9960LITE
import mcp9808

# the name of this device
DEVICE_NAME = '####'

# These should all take i2c as constructor and have a take_measurement method
LIGHT_SENSOR_CLASS = adps9960LITE.APDS9960LITE
TEMP_SENSOR_CLASS = mcp9808.MCP9808

# Wi-Fi network constants
WIFI_SSID = "####SSID"
WIFI_PASSWORD = "####PASWD"

# MQTT client and broker constants
MQTT_CLIENT_KEY = "###.private.key"
MQTT_CLIENT_CERT = "####.cert.pem"

MQTT_BROKER = "#####-ats.iot.us-east-1.amazonaws.com"
MQTT_BROKER_CA = "AmazonRootCA1.pem"

SCL_PIN=17
SDA_PIN=16
