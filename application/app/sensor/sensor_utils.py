""" Generally static utility methods
"""
import importlib
import logging

from . sensor import Sensor

class SensorUtils:

    @staticmethod
    def instance_from_definition(class_definition: dict):
        """Given a string of the ClassName, locate it and create an instance

        Args:
            class_name (str): _description_

        Returns:
            _type_: _description_
        """

        source_module = "app.sensor"
        module = importlib.import_module(source_module)

        class_name = class_definition['class']

        instance = None
        try:
            class_ = getattr(module, class_name)
            args = ()  # not used for now
            kwargs = class_definition['params'] if 'params' in class_definition else {}
            instance = class_(*args, **kwargs)
        except AttributeError as ae:
            logging.error(f"The provided class name {class_name} was not found in {source_module} with error {ae}")

        if isinstance(instance, Sensor):
            return instance
       
        # this includes the None case or any other non-Sensor subclass
        raise ValueError(f"The provided class name {class_name} was not identified as a type of {Sensor} in {source_module}")

    @staticmethod
    def _split_and_clean(config_string: str, delim: str):
        """Take a string and turn it into a list that's clean of empty entries and whitespaces

        Args:
            config_string (str): the string to split and clean
            delim (str): delimiter character

        Returns:
            a cleaned list
        """

        config_list = config_string.split(delim)
        
        # remove any stray spaces
        config_list = [ config.strip() for config in config_list ]
        # remove any empty items - handles both stray commas and overall empty string
        config_list = [ config for config in config_list if len(config) > 0 ]

        return config_list

    @staticmethod
    def sensor_definition_list_from_config_string(sensor_config_string: str):
        """Process a configuration string and return a sensor definition list.

        The sensor string should be of format:
        ClassName(param1=value1,param2=value2);ClassName2(param1=value1)
        and should return a list of format, with
        the value of params passable as **kwargs for sensor constructor (as in __init__(**kwargs) ) 
        [
            {'class': 'ClassName', 'params': {'param1': value1, 'param2': value2}},
            {'class': 'ClassName2', 'params': {'param1': value1}
        ]

        Args:
            sensor_config_string (str): see format noted in description

        Returns:
            sensor_definition_list (list): see format noted in description
        """

        # get the list of individual sensor configurations
        sensor_config_lines = SensorUtils._split_and_clean(sensor_config_string, ';')
        logging.debug(f"List of individual sensor config lines is {sensor_config_lines}")




        sensor_configs = None

        return sensor_configs
