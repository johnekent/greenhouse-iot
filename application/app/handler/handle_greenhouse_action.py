import json
from re import S
import uuid

import boto3

def _message(client, msg_id, watering_zone, watering_minutes, topic = "greenhouse/control"):
    
    payload = json.dumps({"command":"water", "zone": watering_zone, "duration": watering_minutes, "msg_id": msg_id})
    
    # Change topic, qos and payload
    response = client.publish(
        topic=topic,
        qos=1,
        payload=payload
    )
    
    print(f"Published {payload} to topic {topic}")

def _get_float_state(sensor_metrics: dict, float_name: str):

    state_tag = 'float_switch_state'

    float_state = "UNKNOWN"

    if float_name in sensor_metrics:
        float_el = sensor_metrics[float_name]
        if state_tag in float_el:
            float_state = float_el[state_tag]

    return float_state

def _get_value_if_else(source, key, default):
    """Utility function to get the value if it's on the source otherwise return the default

    Args:
        source (dict): The source of key with value
        key (str): The key of the value
        default (): The default if key not found

    Returns:
        _type_: _description_
    """
    value = source[key] if key in source else default
    return value

def lambda_handler(event, context):
    print(f"Receieved event {event} with context {context}")
    
    location = _get_value_if_else(event, 'location', "Mysterious")
    volume_gallons =  _get_value_if_else(event, 'volume_gallons', "-1")
    msg_id = _get_value_if_else(event, 'msg_id', f"handler-{str(uuid.uuid4())}")
    sensor_metrics = _get_value_if_else(event, 'sensor_metrics', {})

    print(f"Sensor metrics = {sensor_metrics}")
    
    ### the rule will filter out the HIGH or LOW
    float_switch_left = _get_float_state(sensor_metrics, 'float_switch_left')
    float_switch_right = _get_float_state(sensor_metrics, 'float_switch_right')
    
    print(f"The location of event is {location} with volume {volume_gallons} and float_switch_left {float_switch_left} : float_switch_right {float_switch_right}")

    client = boto3.client('iot-data', region_name='us-east-1')
    print(f"Created iot-data client {client}")


    ### determine what zone and what duration
    if float_switch_left == "LOW":
        watering_zone = 1
        watering_minutes = 1
        print(f"Initiating command to add water to zone {watering_zone} for {watering_minutes} minutes.")

        _message(client, msg_id, watering_zone, watering_minutes)
        
    if float_switch_right == "LOW":
        watering_zone = 4
        watering_minutes = 1
        print(f"Initiating command to add water to zone {watering_zone} for {watering_minutes} minutes.")
        
        _message(client, msg_id, watering_zone, watering_minutes)

    return {
        'statusCode': 200,
        'body': json.dumps('Successfully received.  Please see topic for instruction.')
    }
