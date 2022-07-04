# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0.
""" driver.py

Creates sensor and attaches to control plane
"""

import argparse
import logging
import threading
from uuid import uuid4

from awscrt import io

from sensor_publisher import SensorPublisher

# This sample uses the Message Broker for AWS IoT to send and receive messages
# through an MQTT connection. On startup, the device connects to the server,
# subscribes to a topic, and begins publishing messages to that topic.
# The device should receive those same messages back from the message broker,
# since it is subscribed to that same topic.

parser = argparse.ArgumentParser(description="Send and receive messages through and MQTT connection.")
parser.add_argument('--endpoint', required=True, help="Your AWS IoT custom endpoint, not including a port. " +
                                                      "Ex: \"abcd123456wxyz-ats.iot.us-east-1.amazonaws.com\"")
parser.add_argument('--port', type=int, help="Specify port. AWS IoT supports 443 and 8883.")
parser.add_argument('--cert', help="File path to your client certificate, in PEM format.")
parser.add_argument('--key', help="File path to your private key, in PEM format.")
parser.add_argument('--root-ca', help="File path to root certificate authority, in PEM format. " +
                                      "Necessary if MQTT server uses a certificate that's not already in " +
                                      "your trust store.")
parser.add_argument('--client-id', default="greenhouse-sensor-" + str(uuid4()), help="Client ID for MQTT connection.")
parser.add_argument('--topic', default="greenhouse/metrics", help="Topic to publish messages to.")
parser.add_argument('--control-topic', default="greenhouse/control", help="Topic to subscribe to for control.")
parser.add_argument('--verbosity', choices=[x.name for x in io.LogLevel], default=io.LogLevel.NoLogs.name,
    help='Logging level')

# Using globals to simplify sample code
args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

io.init_logging(getattr(io.LogLevel, args.verbosity), 'stderr')

if __name__ == '__main__':

    sensor_publisher = SensorPublisher(args.verbosity, args.endpoint, args.port, args.topic, args.control_topic, args.cert, args.key, args.root_ca, args.client_id, seconds_between=120)
    sensor_publisher.start_sensor()

    x = threading.Thread(target=sensor_publisher.subscribe_control_messages, daemon=True)
    x.start()
    print(f"Started control thread as {x}")
