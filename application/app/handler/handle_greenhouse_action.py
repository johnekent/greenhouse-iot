import json
import uuid

import boto3

def _message(client, watering_zone, watering_minutes, topic = "greenhouse/control"):
    
    payload = json.dumps({"command":"water", "zone": watering_zone, "duration": watering_minutes, "msg_id": str(uuid.uuid4())})
    
    # Change topic, qos and payload
    response = client.publish(
        topic=topic,
        qos=1,
        payload=payload
    )
    
    print(f"Published {payload} to topic {topic}")

def lambda_handler(event, context):
    print(f"Receieved event {event} with context {context}")
    
    location = event['location']
    volume_gallons = event['volume_gallons']
    
    sensor_metrics = event['sensor_metrics']
    
    ### the rule will filter out the HIGH or LOW
    float_switch_left = sensor_metrics['float_switch_left']['float_switch_state']
    float_switch_right = sensor_metrics['float_switch_right']['float_switch_state']
    
    print(f"The location of event is {location} with volume {volume_gallons} and float_switch_left {float_switch_left} : float_switch_right {float_switch_right}")

    client = boto3.client('iot-data', region_name='us-east-1')
    print(f"Created iot-data client {client}")


    ### determine what zone and what duration
    if float_switch_left == "LOW":
        watering_zone = 1
        watering_minutes = 1
        print(f"Initiating command to add water to zone {watering_zone} for {watering_minutes} minutes.")

        _message(client, watering_zone, watering_minutes)
        
    if float_switch_right == "LOW":
        watering_zone = 4
        watering_minutes = 1
        print(f"Initiating command to add water to zone {watering_zone} for {watering_minutes} minutes.")
        
        _message(client, watering_zone, watering_minutes)

    return {
        'statusCode': 200,
        'body': json.dumps('Successfully received.  Please see topic for instruction.')
    }
