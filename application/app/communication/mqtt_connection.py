""" mqtt_connection
"""

import logging
import sys

from awscrt import io, mqtt
from awsiot import mqtt_connection_builder



class MQTTConnection:
    """Class MQTTConnection.  Contains the connection and lifecycle of MQTT connection for topic send and receive.
    """
    
    def __init__(self, endpoint, port, cert, key, root_ca, client_id, verbosity=io.LogLevel.NoLogs.name):
        """ Create the class but do not make any connections

        Args:
            endpoint (_type_): MQTT connection endpoint
            port (_type_): MQTT connection port
            cert (_type_): _description_
            key (_type_): _description_
            root_ca (_type_): _description_
            client_id (_type_): _description_
        """

        self.endpoint = endpoint
        self.port = port
        self.cert = cert
        self.key = key
        self.root_ca = root_ca
        self.client_id = client_id

        self.mqtt_connection = None

        ## share the same connection across users
        ## putting this init also prevents synchronization issues across users
        self.mqtt_connection = self.create_connection()

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
        logging.error(f"Received connection ({connection}) interrupted error: {error}.")

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
            mqtt_connection:  connection to the actual MQTT service

        """

        if self.mqtt_connection:
            logging.warning(f"Create connection was called but an existing connection already exists.  Retaining existing connection.")
            return

        # Spin up resources
        event_loop_group = io.EventLoopGroup(num_threads=1)
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

        return mqtt_connection        

    def publish_message(self, topic, message):
        """Write message to topic using connection

        Args:
            mqtt_connection (_type_): _description_
            topic (_type_): _description_
            message (_type_): _description_

        Raises:
            ValueError: _description_
        """

        if not self.mqtt_connection:
            self.create_connection()

        if not isinstance(message, str):
            raise ValueError(f"Expected string argument for message but got {type(message)}")

        #TODO:  add error handling and resiliency for loss of network connection to publish
        result = self.mqtt_connection.publish(topic=topic, payload=message, qos=mqtt.QoS.AT_LEAST_ONCE)
        logging.info(f"Published message {message} to topic {topic} with result {result}")


    def subscribe_to_messages(self, subscribe_topic, callback):
        """Subscribe to control messages and set the callback (on_message_received)
        """

        if not self.mqtt_connection:
            self.create_connection()

        logging.info(f"Subscribing to topic {subscribe_topic}")
        subscribe_future, packet_id = self.mqtt_connection.subscribe(
            topic=subscribe_topic,
            qos=mqtt.QoS.AT_MOST_ONCE,  # do not let a message go more than one time in our context
            callback=callback)

        subscribe_result = subscribe_future.result()
        logging.info(f"Subscribed with {subscribe_result['qos']} to {subscribe_topic} using callback {str(callback)}")
