"""
SensorPublisher

Take measurements and put to MQTT.
Accepts messages from control MQTT.
"""

import json
import random
import sys
from threading import Timer

from awscrt import io, mqtt
from awsiot import mqtt_connection_builder

from Temp_Humidity_Sensor import TempHumiditySensor
from Light_Sensor import LightSensor
from Water_Probe import WaterProbe
class RepeatTimer(Timer):
    """class RepeatTimer

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)
class SensorPublisher:
    """Handles the sensing and publishing
    """

    def __init__(self, verbosity, endpoint, port, topic, control_topic, cert, key, root_ca, client_id, seconds_between=10):
        """_summary_

        Args:
            verbosity (_type_): _description_
            endpoint (_type_): MQTT connection endpoint
            port (_type_): MQTT connection port
            topic (_type_): Publish measurement messages to this topic
            control_topic (_type_): Receive control messages from this topic
            cert (_type_): _description_
            key (_type_): _description_
            root_ca (_type_): _description_
            client_id (_type_): _description_
            seconds_between (int, optional): Time between measurements.  Defaults to 10.
        """
        self.reading_timer = None
        self.endpoint = endpoint
        self.port = port
        self.topic = topic
        self.control_topic = control_topic
        self.cert = cert
        self.key = key
        self.root_ca = root_ca
        self.client_id = client_id
        self.seconds_between = seconds_between

        io.init_logging(getattr(io.LogLevel, verbosity), 'stderr')
        print(f"Initializing the measuring publisher.  Messages sent to topic {self.topic} and controls receieved from topic {self.control_topic}")

        self.mqtt_connection = self.create_connection(endpoint, port, cert, key, root_ca, client_id)

        # If there is an exception on creating these then let it fail
        self.temp_humidity_sensor = TempHumiditySensor()
        self.light_sensor = LightSensor()
        self.water_probe = WaterProbe()

    def publish_metrics(self, mqtt_connection, topic, message):
        """Write message to topic using connection

        Args:
            mqtt_connection (_type_): _description_
            topic (_type_): _description_
            message (_type_): _description_

        Raises:
            ValueError: _description_
        """

        if not isinstance(message, str):
            raise ValueError(f"Expected string argument for message but got {type(message)}")

        result = mqtt_connection.publish(topic=topic, payload=message, qos=mqtt.QoS.AT_LEAST_ONCE)
        print(f"Published message {message} to topic {topic} with result {result}")

    def measure_environment(self):
        """Call all of the sensors to take measurements

        Returns:
            dict: location, volume_gallons, temp_humidity (from get_temp_humidity_metrics), light (from get_light_metrics), water (from get_water_temp_metrics)
        """
        volume_reading = random.uniform(0, 5)

        ### read sensor data
        th_metrics = self.SensorPublisher.read()
        light_metrics = self.light_sensor.read()
        water_metrics = self.water_probe.read()

        message = {"location": "hydro_1", "volume_gallons": volume_reading, "temp_humidity": th_metrics, "light": light_metrics, "water": water_metrics}
        print(f"Measured {message}")
        return message

    def send_measurement(self):
        """A method that takes and publishes metrics.
        This is the single method invoked by the RepeatTimer
        """
        message = self.measure_environment()
        self.publish_metrics(self.mqtt_connection, self.topic, json.dumps(message))

    ### Timer and Topic Configuration
    def start_sensor(self):
        """Create the timer and start it
        """
        if not self.reading_timer:
            self.reading_timer = RepeatTimer(self.seconds_between, self.send_measurement)

        self.reading_timer.start()

    def stop_sensor(self):
        """Cancel the timer
        """
        print("Stopping sensor timer")
        self.reading_timer.cancel()

    def subscribe_control_messages(self):
        """Subscribe to control messages and set the callback (on_message_received)
        """
        # Subscribe
        subscribe_topic = self.control_topic
        print(f"Subscribing to topic {subscribe_topic}")
        subscribe_future, packet_id = self.mqtt_connection.subscribe(
            topic=subscribe_topic,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=self.on_message_received)

        subscribe_result = subscribe_future.result()
        print(f"Subscribed with {subscribe_result['qos']}")

    def disconnect_mqtt(self):
        """Disconnect from mqtt
        """
        # Disconnect
        print("Disconnecting...")
        disconnect_future = self.mqtt_connection.disconnect()
        disconnect_future.result()
        print("Disconnected from MQTT!")

    @staticmethod
    def on_connection_interrupted(connection, error, **kwargs):
        """ Callback when connection is accidentally lost.

        Args:
            connection (_type_): MQTT connection
            error (_type_): The error from the disconnect
        """
        print(f"Connection interrupted. error: {error}")

    @staticmethod
    def on_resubscribe_complete(resubscribe_future):
        """Callback when resubscribe to topic is completed

        Args:
            resubscribe_future (_type_): _description_
        """
        resubscribe_results = resubscribe_future.result()
        print(f"Resubscribe results: {resubscribe_results}")

        for topic, qos in resubscribe_results['topics']:
            if qos is None:
                sys.exit(f"Server rejected resubscribe to topic: {topic}")

    @staticmethod
    def on_connection_resumed(connection, return_code, session_present, **kwargs):
        """ Callback when an interrupted connection is re-established.

        Args:
            connection (_type_): _description_
            return_code (_type_): _description_
            session_present (_type_): _description_
        """
        print(f"Connection resumed. return_code: {return_code} session_present: {session_present}")

        if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
            print("Session did not persist. Resubscribing to existing topics...")
            resubscribe_future, _ = connection.resubscribe_existing_topics()

            # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
            # evaluate result with a callback instead.
            resubscribe_future.add_done_callback(SensorPublisher.on_resubscribe_complete)

    def on_message_received(self, topic, payload, dup, qos, retain, **kwargs):
        """ Callback when the subscribed topic receives a message from the control topic
        Handles the control topic message (such as stop_sensor or start_sensor)

        Args:
            topic (_type_): _description_
            payload (_type_): _description_
            dup (_type_): _description_
            qos (_type_): _description_
            retain (_type_): _description_
        """
        print(f"Received {payload} from topic {topic}")
        payload_json = json.loads(payload)
        command = payload_json['command']
        print(f"Received control command {command}")
        if command == 'stop_sensor':
            print("---------------Receieved command to stop sensor")
            self.stop_sensor()
        elif command == 'start_sensor':
            print("---------------Receieved command to start sensor")
            self.start_sensor()
        else:
            print(f"Received unknown command {command}")

    def create_connection(self, endpoint, port, cert, key, root_ca, client_id):
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
