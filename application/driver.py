# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0.
""" driver.py

Creates sensor and attaches to control plane
"""

import argparse
import configparser
import logging
import threading
import asyncio
from uuid import uuid4

from awscrt import io
from actuator_processor import ActuatorProcessor
from sensor_publisher import SensorPublisher

from app.communication import MQTTConnection

# This sample uses the Message Broker for AWS IoT to send and receive messages
# through an MQTT connection. On startup, the device connects to the server,
# subscribes to a topic, and begins publishing messages to that topic.
# The device should receive those same messages back from the message broker,
# since it is subscribed to that same topic.

parser = argparse.ArgumentParser(description="Send and receive messages through and MQTT connection.")
parser.add_argument('--port', type=int, help="Specify port. AWS IoT supports 443 and 8883.")
parser.add_argument('--topic', default="greenhouse/metrics", help="Topic to publish messages to.")
parser.add_argument('--control-topic', default="greenhouse/control", help="Topic to subscribe to for control.")
parser.add_argument('--verbosity', choices=[x.name for x in io.LogLevel], default=io.LogLevel.NoLogs.name,
    help='Logging level')

# Using globals to simplify sample code
args = parser.parse_args()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')

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

    sensor_publisher = SensorPublisher(
        mqtt_connection = mqtt_connection,
        topic = args.topic,
        seconds_between=polling_interval,
        thing_name=thing_name,
        active_sensors=active_sensors)

    sensor_publisher.start_sensor()

    ## Note:  This is currently setup to run on the same device (sensor and actuator).
    # However, it could be split out to separate devices which would require a change to driver.

    actuator_processor = ActuatorProcessor(water_actuator_address=melnor_mac)
    control_topic=args.control_topic

    #control_thread = threading.Thread(target=mqtt_connection.subscribe_to_messages, args=[], kwargs={'subscribe_topic': control_topic, 'callback': actuator_processor.on_message_received}, daemon=True)
    #control_thread.start()
    #logging.info(f"Started control thread as {control_thread}")

    mqtt_connection.subscribe_to_messages(subscribe_topic=control_topic, callback=actuator_processor.on_message_received)
    logging.info(f"Registered subscription to {control_topic} for callback {actuator_processor.on_message_received}")

    # don't exit
    try:
        loop = asyncio.get_event_loop()
        loop.run_forever()
    except KeyboardInterrupt as ki:
        pass
    finally:
        logging.info(f"The control loop is now closing due to receiving {ki}")
        loop.close()

    print("Finished")
