import pytest

import asyncio

from ..context import app

from app.actuator import WaterActuator

class MockValve:
    """Mock out the underlying valve
    """
    def __init__(self, id, is_watering, manual_watering_minutes, watering_end_time):
        """constructor

        Args:
            id (int): the 0-3 index of the valve
            is_watering (bool): _description_
            manual_watering_minutes (int): seconds to water for
            watering_end_time (milliseconds epoch when end): _description_
        """
        self.id = id
        self.is_watering = is_watering
        self.manual_watering_minutes = manual_watering_minutes
        self.watering_end_time = watering_end_time


class MockDevice:
    """Mock out the underlying device
    """
    def __init__(self, battery_level, zone1, zone2, zone3, zone4):
        """constructor

        Args:
            battery_level (int): _description_
            zone1-4 (MockValve): _description_
        """
        self.battery_level = battery_level
        self.zone1 = zone1
        self.zone2 = zone2
        self.zone3 = zone3
        self.zone4 = zone4

def test_get_device_status():
    zones = [ MockValve(i, False, 1, 1000) for i in range(0, 4) ]
    device = MockDevice(battery_level=100, zone1=zones[0], zone2=zones[1], zone3=zones[2], zone4=zones[3])

    status =  WaterActuator.get_device_status(device)

    assert isinstance(status, dict)

def test_get_device_status_battery():
    zones = [ MockValve(i, False, 1, 1000) for i in range(0, 4) ]
    battery = 85
    device = MockDevice(battery_level=battery, zone1=zones[0], zone2=zones[1], zone3=zones[2], zone4=zones[3])

    status =  WaterActuator.get_device_status(device)

    returned_battery = status['battery_level']

    assert battery == returned_battery

def test_get_device_status_valve():
    zones = [ MockValve(i, False, 1, 1000) for i in range(0, 4) ]
    
    zone1_is_watering = True
    zone2_manual_watering_minutes = 14
    zone3_watering_end_time = 812516188
    zone4_manual_watering_minutes = 116

    zones[0].is_watering = zone1_is_watering
    zones[1].manual_watering_minutes = zone2_manual_watering_minutes
    zones[2].watering_end_time = zone3_watering_end_time
    zones[3].manual_watering_minutes = zone4_manual_watering_minutes
 
    device = MockDevice(battery_level=100, zone1=zones[0], zone2=zones[1], zone3=zones[2], zone4=zones[3])
 
    status =  WaterActuator.get_device_status(device)

    print(status)

    returned_valves = status['valves']

    assert zone1_is_watering == returned_valves['valve1']['is_watering']
    assert zone2_manual_watering_minutes == returned_valves['valve2']['manual_watering_minutes']
    assert zone3_watering_end_time == returned_valves['valve3']['watering_end_time']
    assert zone4_manual_watering_minutes == returned_valves['valve4']['manual_watering_minutes']

def test_is_watering():
    valve = MockValve(1, is_watering=False, manual_watering_minutes=0, watering_end_time=0)
    assert not WaterActuator.is_watering(valve)

    valve = MockValve(1, is_watering=True, manual_watering_minutes=0, watering_end_time=0)
    assert WaterActuator.is_watering(valve)


tests = [ 
    ("'PP:PP:PP:PP:PP:PP'", False),
    ("38:9F:DE:A8:80:36", True),
    ("'38:9F:DE:A8:80:36'", False),
 ]
@pytest.mark.parametrize('sample, expected', tests)
def test_is_valid_address(sample, expected):

    assert WaterActuator.is_valid_address(sample) == expected


def test_water_zone_protects_watering_active(monkeypatch):
    """There could be scenarios where an automated timer is already going, OR
    cases where the central command tells to re-water something that's already manually being watered.
    So, don't issue a new watering command if one is already in progress.
    """

    # this test gets quite involved as it depends a lot on the device being there and mocking it entirely is a hassle
    NotImplemented
