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

        try:
            self.connection = self._connect()
            logging.debug(f"Created connection in {self}")
        except RuntimeError as rte:
            logging.error(f"Initiating {self} received error {rte}.  Will try again with each read.")

        super(Sensor,self).__init__(*args, **kwargs)

    def read(self):
        """Provide central logic of getting information from a physical device, as returned by _read()

        If the connection does not already exist try to create it.
        If the connection does exist and gives a failure on read, unset the connection for next time.

        Returns:
            json: The content returned by the read.
        """

        # explicit default
        message = None

        if not self.connection:
            try:
                self.connection = self._connect()
                logging.debug(f"Within read created connection in {self}")
            except RuntimeError as rte:
                logging.error(f"Connecting on read in {self} received error {rte}.  Will try again with each read.")
        
        # if successful use it
        if self.connection:
            try:
                message = self._read()
                logging.debug(f"Within read in {self} retrieved {message}")
            except RuntimeError as rte:
                logging.error(f"Attempting read in {self} on connection {rte}.  Unsetting the connection.")
                # if not successful, initiate a reconnect on the connection
                self.connection = None

        return message

    @abstractmethod
    def _read():
        """ Read from implemented Sensor and return data in json format
        The read should be done from the connection returned in _connect()

        Returns:
            json: the message from the sensor
        Raises:
            any exception that occurs in the form of a RuntimeError
        """ 
        pass

    @abstractmethod
    def _connect():
        """ Create a connection to the device from which to _read()
        If connection fails let the exception raise.
        Generate exceptions as RuntimeExceptions.
        """ 
        pass

    @abstractmethod
    def _name():
        """ An (ideally unique) name to identify the implemented sensor.
        """
        pass
