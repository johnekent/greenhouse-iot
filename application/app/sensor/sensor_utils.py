""" Generally static utility methods
"""
from email.headerregistry import ParameterizedMIMEHeader
import importlib
import logging
import re

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

        assert isinstance(config_string, str), f"The parameter {config_string} must be a string"

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
        ClassName(param1=value1,param2=value2);ClassName2(param1=value1);ClassName3
        and should return a list of format, with
        the value of params passable as **kwargs for sensor constructor (as in __init__(**kwargs) ) 
        [
            {'class': 'ClassName', 'params': {'param1': value1, 'param2': value2} },
            {'class': 'ClassName2', 'params': {'param1': value1} },
            {'class': 'ClassName3' }
        ]

        Args:
            sensor_config_string (str): see format noted in description

        Returns:
            sensor_definition_list (list): see format noted in description
        """

        # get the list of individual sensor configurations
        sensor_config_lines = SensorUtils._split_and_clean(sensor_config_string, ';')
        logging.debug(f"List of individual sensor config lines is {sensor_config_lines}")

        sensor_definition_list = []

        ## e.g. ClassName(stuffstuffstuff)
        class_with_params_pattern = r"(.+)\((.+)\)$"  # The r handles the escape \( without warning

        for sensor_config in sensor_config_lines:
            class_name = None
            params = None
            if re.match(class_with_params_pattern, sensor_config):
                ## slice it out
                params_string = sensor_config[sensor_config.find('(')+1:sensor_config.find(')')]
                params_list = SensorUtils._split_and_clean(params_string, ",")
                # style note:  list and dict comprehension here with the function calls would be hard to read and harder to debug
                # ... hence the for loops
                params = {}
                class_name = sensor_config.split("(")[0]
                for param in params_list:
                    kvp_list = SensorUtils._split_and_clean(param, "=")
                    if len(kvp_list) == 2:
                        params[kvp_list[0]] = kvp_list[1]
                    else:
                        logging.warning(f"The parameter configuration of {param} for class {class_name} did not match expected pattern of key=value.")

            else:
                class_name = sensor_config

            sensor_definition = {}
            sensor_definition['class']=class_name
            if params:
                sensor_definition['params']= params
            sensor_definition_list.append(sensor_definition)

        return sensor_definition_list
