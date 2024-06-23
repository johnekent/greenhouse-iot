""" actuator_processor.py
Handle receipt and processing of control messages on topics
"""

import json
import logging
import asyncio
import boto3

from app.actuator import WaterActuator

class ActuatorProcessor:
    """ Receive messages and issue commands.
    """

    def __init__(self, water_actuator_address: str):
        self.water_actuator_address = water_actuator_address
        logging.info(f"Initiatlized {self} with water_actuator_address {water_actuator_address}")

    def on_message_received(self, topic, payload):
        """ Callback when the subscribed topic receives a message from the control topic
        Handles the control topic message (such as water a zone)

        Args:
            topic (_type_): _description_
            payload (_type_): _description_
        """
        logging.info(f"Received {payload} from topic {topic}")
        payload_json = json.loads(payload)
        command = payload_json['command']
        logging.info(f"Received control command {command}")

        ### there are several zones.
        ### let the central command tell which zone to water.

        # {"command":"water", "zone": watering_zone, "duration": watering_minutes}
        if command == "water":
            zone = payload_json['zone']
            duration = payload_json['duration']

            water_actuator = WaterActuator(address=self.water_actuator_address)
            response = asyncio.run(water_actuator.water_zone(zone=zone, minutes=duration))
            logging.info(f"Sent watering request to {water_actuator} and received response {response}")

            ## TODO assess hackiness of this convenient logging
            try:
                client = boto3.client('iot-data')
                payload = {"command": command, "zone": zone, "duration": duration, "response": response}
                response = client.publish(
                    topic='greenhouse/actions',
                    qos=1,
                    payload=payload
                )
            except Exception as e:
                logging.error(f"Attempted to log the action but got error: {e}.  Oh well.")
