import pytest

from ..context import app

from app.sensor import Sensor
from app.sensor import SensorUtils as su

def test_instance_from_definition():

    definition = {'class': 'LightSensor'}
    instance = su.instance_from_definition(definition)

    assert isinstance(instance, Sensor)

def test_instance_from_definition_name_parameter():

    name = 'floaty_boy'
    definition = {'class': 'FloatSwitchSensor', 'params': {'name': name}}
    instance = su.instance_from_definition(definition)

    assert isinstance(instance, Sensor)
    assert instance.name == name

def test_instance_from_definition_invalid_class():

    definition = {'class': 'TheGreatestOfAllNonexistentSensors'}

    with pytest.raises(ValueError):
        su.instance_from_definition(definition)


#[{'class': 'ClassName', 'params': {'param1': value1, 'param2': value2}}, {'class': 'ClassName2', 'params': {'param1': value1} ]

tests = [ 
    ("LightSensor(name=lighty_boy);", [ {'class': 'LightSensor', 'params': {'name': 'lighty_boy'}} ]),
    ("LightSensor(name=lighty_boy);   KelvinSensor(roo=temparoo);", [ {'class': 'LightSensor', 'params': {'name': 'lighty_boy'}}, {'class': 'KelvinSensor', 'params': {'roo': 'temparoo'}} ])
]
@pytest.mark.parametrize('sensor_list_string, expected_sensor_config', tests)
def test_sensor_definition_list_from_config_string(sensor_list_string, expected_sensor_config):
    
    sensor_list = su.sensor_definition_list_from_config_string(sensor_list_string)

    assert len(sensor_list) == len(expected_sensor_config)

## rather than doing a bunch of confusing zips and lists, just to some targeted tests
def test_sensor_definition_list_from_config_string_has_no_params():

    sensor_list = su.sensor_definition_list_from_config_string("LightSensor(name=lighty_boy);")
    assert 'params' not in sensor_list[0]

def test_sensor_definition_list_from_config_string_has_dict_entries():
    sensor_list = su.sensor_definition_list_from_config_string("LightSensor(name=lighty_boy);")

    assert isinstance(sensor_list, list)
    assert isinstance(sensor_list[0], dict)


def test_sensor_definition_list_from_config_string_has_matching_params():

    class_name = "jhh126162"
    k1 = "asdfasfd"
    v1 = "161d8"
    k2 = "9271616"
    v2 = "78699716"

    config_string = f"{class_name}({k1}={v1},{k2}={v2}"
    sensor_list = su.sensor_definition_list_from_config_string(config_string)

    sensor_config = sensor_list[0]

    #assert sensor_list['class'] == class_name


def test_split_and_clean():
    result = su._split_and_clean("asdfasd; ;    ;", ";")

    assert len(result) == 1

def test_constructor_args():
    """confirm that kwargs passed through constructors work
    """
    from app.sensor import FloatSwitchSensor

    args = ()
    kwargs={'name': "floatyboy"}
    f = FloatSwitchSensor(*args, **kwargs)

    assert f.name == "floatyboy"
