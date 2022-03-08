# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0.

import argparse
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import sys
import threading
import time
from uuid import uuid4
import json
import random
from threading import Timer

class SensorPublisher:

    def __init__(self, verbosity, endpoint, port, cert, key, root_ca, client_id, seconds_between=10):
        self.reading_timer = None
        self.endpoint = endpoint
        self.port = port
        self.cert = cert
        self.key = key
        self.root_ca = root_ca
        self.client_id = client_id
        self.seconds_between = seconds_between

        io.init_logging(getattr(io.LogLevel, verbosity), 'stderr')
        print("Initializing")

        self.mqtt_connection = self.create_connection(endpoint, port, cert, key, root_ca, client_id)

    ### Sensor functionality
    def publish_volume(self, mqtt_connection, topic, message):

        if not isinstance(message, str):
            raise ValueError(f"The argument for message must be a string but it was {type(message)}")

        print(f"Publishing message {message} to topic {topic}")
        result = mqtt_connection.publish(topic=topic, payload=message, qos=mqtt.QoS.AT_LEAST_ONCE)
        print(f"The result of publish is {result}")

    def measure_volume(self):
        volume_reading = random.uniform(0, 5)
        message = {"location": "hydro_1", "volume_gallons": volume_reading}
        print(f"Measured {message}")
        return message        

    def send_measurement(self):
        message = self.measure_volume()
        self.publish_volume (self.mqtt_connection, self.topic, json.dumps(message))


    ### Timer and Topic Configuration
    def start_sensor(self):
        if not self.reading_timer:
            self.reading_timer = Timer(self.seconds_between, self.send_measurement)
        self.reading_timer.start()

    def subscribe_control_messages(self):
        # Subscribe
        print(f"Subscribing to topic {self.topic}")
        subscribe_future, packet_id = self.mqtt_connection.subscribe(
            topic=self.topic,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=self.on_message_received)

        subscribe_result = subscribe_future.result()
        print(f"Subscribed with {subscribe_result['qos']}")

    def disconnect_mqtt(self):
        # Disconnect
        print("Disconnecting...")
        disconnect_future = self.mqtt_connection.disconnect()
        disconnect_future.result()
        print("Disconnected!")

    # Callback when connection is accidentally lost.
    def on_connection_interrupted(connection, error, **kwargs):
        print(f"Connection interrupted. error: {error}")

    def on_resubscribe_complete(resubscribe_future):
        resubscribe_results = resubscribe_future.result()
        print(f"Resubscribe results: {resubscribe_results}")

        for topic, qos in resubscribe_results['topics']:
            if qos is None:
                sys.exit(f"Server rejected resubscribe to topic: {topic}")

    # Callback when an interrupted connection is re-established.
    def on_connection_resumed(connection, return_code, session_present, **kwargs):
        print(f"Connection resumed. return_code: {return_code} session_present: {session_present}")

        if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
            print("Session did not persist. Resubscribing to existing topics...")
            resubscribe_future, _ = connection.resubscribe_existing_topics()

            # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
            # evaluate result with a callback instead.
            resubscribe_future.add_done_callback(SensorPublisher.on_resubscribe_complete)

    # Callback when the subscribed topic receives a message
    def on_message_received(topic, payload, dup, qos, retain, **kwargs):
        print(f"Received {payload} from topic {topic}")
        print(f"The arguments into message received were {kwargs}")

    def create_connection(endpoint, port, cert, key, root_ca, client_id):
        """_summary_

        Args:
            endpoint (_type_): _description_
            port (_type_): _description_
            cert (_type_): _description_
            key (_type_): _description_
            root_ca (_type_): _description_
            client_id (_type_): _description_

        Returns:
            _type_: _description_
        """
        # Spin up resources
        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

        # not using websocket
        mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=endpoint,
            port=port,
            cert_filepath=cert,
            pri_key_filepath=key,
            client_bootstrap=client_bootstrap,
            ca_filepath=root_ca,
            on_connection_interrupted=SensorPublisher.on_connection_interrupted,
            on_connection_resumed=SensorPublisher.on_connection_resumed,
            client_id=client_id,
            clean_session=False,
            keep_alive_secs=30,
            http_proxy_options=None)

        print(f"Connecting to {endpoint} with client ID [{client_id}] through {mqtt_connection}...")
        connect_future = mqtt_connection.connect()
        # Future.result() waits until a result is available
        result = connect_future.result()
        print(f"Connected with result {result}!")

        return mqtt_connection
