import pytest

from tests import ignore_sensor_modules

from sensor_publisher import SensorPublisher

all_known_sensors = "TempHumiditySensor; TempHumiditySensorI2C; LightSensor; LightSensorUV; WaterProbe; FloatSwitchSensor"

def test_load_empty_sensors_list():

    sensors = SensorPublisher.load_sensors("")

    assert isinstance(sensors, list)
    assert len(sensors) == 0

def test_load_sensors_list_spaces_ok():
    #test with a space between
    sensors = SensorPublisher.load_sensors(all_known_sensors)

    assert len(sensors) == len(all_known_sensors.split(";"))

### This is a broad test of functionality
def test_load_sensors_list_sensor_names():
    
    test_name = "9kkjlahsgl2146246"
    named_sensors = f"TempHumiditySensor(name={test_name}); TempHumiditySensorI2C(name={test_name}); LightSensor(name={test_name}); LightSensorUV(name={test_name}); WaterProbe(name={test_name}); FloatSwitchSensor(name={test_name})"

    sensors = SensorPublisher.load_sensors(named_sensors)

    for sensor in sensors:
        assert test_name == sensor._name(), f"Expected to see test name of {test_name} but instead it was {sensor._name()}"

    assert len(sensors) == len(all_known_sensors.split())


def test_load_sensors_mix_of_bad_and_good_throws_exception():

    with pytest.raises(ValueError):
        sensors = SensorPublisher.load_sensors(all_known_sensors + ",SomeJunkyThing")

def test_measure_environment(monkeypatch):
    """This tests that the class really loads and that it can generally operate without interacting with the environment

    Args:
        monkeypatch (_type_): _description_
    """

    def mock_create_connection(self, endpoint, port, cert, key, root_ca, client_id):
        return None

    # don't try to make a connection as it will not work
    # monkeypatch.setattr(SensorPublisher, "create_connection", mock_create_connection)  <-- moved out of this class
    
    sp = SensorPublisher(mqtt_connection=None, topic=None, thing_name=None, active_sensors="")

    message = sp.measure_environment()
    assert isinstance(message, dict)
