"""E2E test to check the permisssions and connectivity from sensor to lambda to actuator
"""

import argparse
import configparser
from errno import WSAEDQUOT
import logging
import threading
from uuid import uuid4

from awscrt import io

from app.communication import MQTTConnection

parser = argparse.ArgumentParser(description="Send and receive messages through and MQTT connection.")
parser.add_argument('--port', type=int, help="Specify port. AWS IoT supports 443 and 8883.")
parser.add_argument('--topic', default="greenhouse/metrics", help="Topic to publish messages to.")
parser.add_argument('--control-topic', default="greenhouse/control", help="Topic to subscribe to for control.")
parser.add_argument('--verbosity', choices=[x.name for x in io.LogLevel], default=io.LogLevel.NoLogs.name,
    help='Logging level')

# Using globals to simplify sample code
args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

io.init_logging(getattr(io.LogLevel, args.verbosity), 'stderr')

if __name__ == '__main__':

    config_file = '/home/pi/iot/config.ini'
    config = configparser.ConfigParser()
    configs = config.read(config_file)

    if not configs:
        logging.critical("Configuration file must be provided")
        raise RuntimeError(f"A file with relevant values must be at {config_file}")
    
    default_config = config['DEFAULT']
    if not default_config:
        logging.critical("Configuration file must be provided with a DEFAULT section")
        raise RuntimeError(f"A file with relevant values in DEFAULT section must be at {config_file}")
    
    # TODO:  add meaningful error handling around missing values -- can a description be placed in the file and read out here?
    thing_name = default_config['thing_name']
    polling_interval = int(default_config['polling_interval'])
    active_sensors = default_config['active_sensors']
    root_ca = default_config['ROOT_CA']
    key = default_config['KEY']
    cert = default_config['CERT']
    endpoint = default_config['ENDPOINT']

    melnor_mac = default_config['MELNOR_MAC']

    # Client ID for MQTT connection
    client_id = f"greenhouse-sensor-{str(uuid4())}-{thing_name}"
    mqtt_connection = MQTTConnection(
        endpoint=endpoint,
        port=args.port,
        cert=cert,
        key=key,
        root_ca=root_ca,
        client_id=client_id,
        verbosity=args.verbosity)

    base_message = {"location": "pi_zero_2_w", "volume_gallons": 1.272841624348457, "sensor_metrics": {"float_switch": {"float_switch_state": None}}}
    state = base_message['sensor_metrics']['float_switch']['float_switch_state']

    import random

    def subscriber_callback(client, userdata, message):
        print("Received a new message: ")
        print(message.payload)
        print("from topic: ")
        print(message.topic)
        print("--------------\n\n")

    mqtt_connection.subscribe_to_messages(subscribe_topic='greenhouse/command', callback=subscriber_callback)

    for i in range(0, 100):

        rand = random.randint(0, 10)

        state = "HIGH" if rand == 3 else "LOW"
        print(f">>>>>>>>>>>>>>>>>>>>>>>>>>>> {i}:  Publishing message {base_message}")
