""" Generally static utility methods
"""
import importlib
import logging

from . sensor import Sensor

class SensorUtils:

    def instance_from_string(class_name: str):
        """Given a string of the ClassName, locate it and create an instance

        Args:
            class_name (str): _description_

        Returns:
            _type_: _description_
        """

        source_module = "app.sensor"
        module = importlib.import_module(source_module)

        instance = None
        try:
            class_ = getattr(module, class_name)
            instance = class_()
        except AttributeError as ae:
            logging.error(f"The provided class name {class_name} was not found in {source_module} with error {ae}")

        if isinstance(instance, Sensor):
            return instance
        else:  # this includes the None case or any other non-Sensor subclass
            raise ValueError(f"The provided class name {class_name} was not identified as a type of {Sensor} in {source_module}")
