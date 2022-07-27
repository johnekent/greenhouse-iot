"""
SensorPublisher

Take measurements and put to MQTT.  This is the sensor behavior.

"""
from datetime import datetime
import json
import logging
import random
import uuid
from threading import Timer

#TODO:  move this dependency into the MQTT class and refactor
from awscrt import mqtt

from app.sensor import SensorUtils as su

class RepeatTimer(Timer):
    """class RepeatTimer

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    def run(self):

        # run it before waiting to run it more -- probably nicer way to do this but get it done for now
        self.function(*self.args, **self.kwargs)

        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)
class SensorPublisher:
    """Handles the sensing and publishing
    """

    def __init__(self, mqtt_connection, topic, thing_name, active_sensors, seconds_between=10):
        """_summary_

        Args:
            mqtt_connection (AWS mqtt_connection): a connected connection
            topic (str): publish messages to this MQTT topic
            thing_name (str): name of the device
            active_sensors (str): sensor definition configuration
            seconds_between (int, optional): Time between measurements.  Defaults to 10.
        """
        self.reading_timer = None
        self.thing_name = thing_name
        self.seconds_between = seconds_between
        self.active_sensor_instances = SensorPublisher.load_sensors(active_sensors)

        self.mqtt_connection = mqtt_connection
        self.topic = topic
        logging.info(f"Initializing the measuring publisher.  Messages sent to topic {self.topic}.")


    @staticmethod
    def load_sensors(sensor_configuration_string: str):
        """ Create list of instantiated sensor classes based on the list of sensors.

        Args:
            sensor_configuration_string (str): see the definition of sensor_definition_list_from_config_string()

        Returns:
            sensor_class_list (list): list of instantiated sensors
        """

        sensor_definition_list = su.sensor_definition_list_from_config_string(sensor_configuration_string)
        logging.info(f"The cleaned set of sensors is {sensor_definition_list}")

        sensor_class_list = [ su.instance_from_definition(sensor_definition) for sensor_definition in sensor_definition_list ]
        logging.info(f"Using a total of {len(sensor_class_list)} sensors = {sensor_class_list}")

        return sensor_class_list

    def measure_environment(self):
        """Call all of the sensors to take measurements

        Returns:
            dict: location, timestamp fields, volume_gallons, sensor_metrics (from list of sensors)
        """
        volume_reading = random.uniform(0, 5)

        ### read sensor data
        sensor_metrics = { sensor._name() : sensor.read() for sensor in self.active_sensor_instances }

        now = datetime.now()
        ## this is not a nested json because IoT analytics removes the quotes making it hard to separate dates which have formats that really benefit from spaces
        day_and_time = now.strftime("%c")
        day_of_year = now.strftime("%j")
        time_of_day = now.strftime("%H:%M:%S.%f")
        msg_id = str(uuid.uuid4())
        message = {"location": self.thing_name, "datetime": day_and_time, "day_of_year": day_of_year, "time_of_day": time_of_day, "msg_id": msg_id,"volume_gallons": volume_reading, "sensor_metrics": sensor_metrics}
        return message

    def send_measurement(self):
        """A method that takes and publishes metrics.
        This is the single method invoked by the RepeatTimer
        """
        message = self.measure_environment()
        self.mqtt_connection.publish_message(self.topic, json.dumps(message))

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
        logging.info("Stopping sensor timer")
        self.reading_timer.cancel()
