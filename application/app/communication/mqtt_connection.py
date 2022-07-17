""" mqtt_connection
"""

import logging
import sys

from awscrt import io, mqtt
from awsiot import mqtt_connection_builder

class MQTTConnection:
    """Class MQTTConnection.  Contains the connection and lifecycle of MQTT connection for topic send and receive.
    """
    
    def __init__(self, endpoint, port, topic, control_topic, cert, key, root_ca, client_id, verbosity=io.LogLevel.NoLogs.name):
        """ Create the class but do not make any connections

        Args:
            endpoint (_type_): MQTT connection endpoint
            port (_type_): MQTT connection port
            topic (_type_): Publish measurement messages to this topic
            control_topic (_type_): Receive control messages from this topic
            cert (_type_): _description_
            key (_type_): _description_
            root_ca (_type_): _description_
            client_id (_type_): _description_
        """

        self.endpoint = endpoint
        self.port = port
        self.topic = topic
        self.control_topic = control_topic
        self.cert = cert
        self.key = key
        self.root_ca = root_ca
        self.client_id = client_id

        self.mqtt_connection = None

        io.init_logging(getattr(io.LogLevel, verbosity), 'stderr')
    
    def disconnect_mqtt(self):
        """Disconnect from mqtt
        """
        # Disconnect
        logging.debug("Disconnecting...")
        disconnect_future = self.mqtt_connection.disconnect()
        disconnect_future.result()
        logging.info("Disconnected from MQTT!")

    @staticmethod
    def on_connection_interrupted(connection, error, **kwargs):
        """ Callback when connection is accidentally lost.

        Args:
            connection (_type_): MQTT connection
            error (_type_): The error from the disconnect
        """
        logging.error(f"Connection interrupted. error: {error}")

    @staticmethod
    def on_resubscribe_complete(resubscribe_future):
        """Callback when resubscribe to topic is completed

        Args:
            resubscribe_future (_type_): _description_
        """
        resubscribe_results = resubscribe_future.result()
        logging.info(f"Resubscribe results: {resubscribe_results}")

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
        logging.info(f"Connection resumed. return_code: {return_code} session_present: {session_present}")

        if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
            logging.info("Session did not persist. Resubscribing to existing topics...")
            resubscribe_future, _ = connection.resubscribe_existing_topics()

            # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
            # evaluate result with a callback instead.
            resubscribe_future.add_done_callback(MQTTConnection.on_resubscribe_complete)

    def create_connection(self):
        """ Create MQTT connection and register callbacks

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

        if self.mqtt_connection:
            logging.warning(f"Create connection was called but an existing connection already exists.  Returning existing connection.")
            return self.mqtt_connection

        # Spin up resources
        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

        # not using websocket
        mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=self.endpoint,
            port=self.port,
            cert_filepath=self.cert,
            pri_key_filepath=self.key,
            client_bootstrap=client_bootstrap,
            ca_filepath=self.root_ca,
            on_connection_interrupted=self.on_connection_interrupted,
            on_connection_resumed=self.on_connection_resumed,
            client_id=self.client_id,
            clean_session=False,
            keep_alive_secs=30,
            http_proxy_options=None)

        logging.info(f"Connecting to {self.endpoint} with client ID [{self.client_id}] through {mqtt_connection}...")
        connect_future = mqtt_connection.connect()
        # Future.result() waits until a result is available
        result = connect_future.result()
        logging.info(f"Connected with result {result}!")

        self.mqtt_connection = mqtt_connection
        return self.mqtt_connection
        
    def subscribe_to_messages(self, subscribe_topic, callback):
        """Subscribe to control messages and set the callback (on_message_received)
        """
        logging.info(f"Subscribing to topic {subscribe_topic}")
        subscribe_future, packet_id = self.mqtt_connection.subscribe(
            topic=subscribe_topic,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=callback)

        subscribe_result = subscribe_future.result()
        logging.info(f"Subscribed with {subscribe_result['qos']}")
