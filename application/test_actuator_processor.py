import pytest

from tests import ignore_sensor_modules

from actuator_processor import ActuatorProcessor

def test_instantiate():

    a_p = ActuatorProcessor(water_actuator_address=None)
