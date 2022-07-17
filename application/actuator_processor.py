""" actuator_processor.py
Handle receipt and processing of control messages on topics
"""

import json
import logging

class ActuatorProcessor:
    """ Receive messages and issue commands.
    """
    pass

    def on_message_received(self, topic, payload):
        """ Callback when the subscribed topic receives a message from the control topic
        Handles the control topic message (such as stop_sensor or start_sensor)

        Args:
            topic (_type_): _description_
            payload (_type_): _description_
        """
        logging.info(f"Received {payload} from topic {topic}")
        payload_json = json.loads(payload)
        command = payload_json['command']
        logging.info(f"Received control command {command}")
