""" Sensor.py
An abstract class specifying behavior for all Sensors.
This includes connection retry.
"""

from ast import Yield
import logging
from abc import ABC, abstractmethod

class Sensor(ABC):

    def __init__(self, *args, **kwargs):
        self.connection = None

        print(f"calling from {self}")
        try:
            self.connection = self.__connect__()
            logging.debug(f"Created connection in {self}")
        except RuntimeError as rte:
            logging.error(f"Initiating {self} received error {rte}.  Will try again with each read.")

        super(Sensor,self).__init__(*args, **kwargs)

    def read(self):
        """Provide central logic of getting information from a physical device, as returned by __read__()

        If the connection does not already exist try to create it.
        If the connection does exist and gives a failure on read, unset the connection for next time.

        Returns:
            json: The content returned by the read.
        """

        # explicit default
        message = None

        if not self.connection:
            try:
                self.connection = self.__connect__()
                logging.debug(f"Within read created connection in {self}")
            except RuntimeError as rte:
                logging.error(f"Connecting on read in {self} received error {rte}.  Will try again with each read.")
        
        # if successful use it
        if self.connection:
            try:
                message = self.__read__()
                logging.debug(f"Within read in {self} retrieved {message}")
            except RuntimeError as rte:
                logging.error(f"Attempting read in {self} on connection {rte}.  Unsetting the connection.")
                # if not successful, initiate a reconnect on the connection
                self.connection = None

        return message

    @abstractmethod
    def __read__():
        """ Read from implemented Sensor and return data in json format
        The read should be done from the connection returned in __connect__()

        Returns:
            json: the message from the sensor
        Raises:
            any exception that occurs in the form of a RuntimeError
        """ 
        pass

    @abstractmethod
    def __connect__():
        """ Create a connection to the device from which to __read__()
        If connection fails let the exception raise.
        Generate exceptions as RuntimeExceptions.
        """ 
        pass
