import json
import boto3

def lambda_handler(event, context):
    print(f"Receieved event {event} with context {context}")
    
    location = event['location']
    volume_gallons = event['volume_gallons']
    float_swtich = event['sensor_metrics']['float_switch']['float_switch_state']
    
    print(f"The location of event is {location} with volume {volume_gallons} and float_switch {float_swtich}")
    

    client = boto3.client('iot-data', region_name='us-east-1')
    print(f"Created iot-data client {client}")
    
    topic = "greenhouse/command"
    
    ### the rule will filter out the HIGH or LOW
    ### this should determine what zone and what duration
    
    watering_zone = 1
    watering_minutes = 1
    print(f"Initiating command to add water to zone {watering_zone} for {watering_minutes} minutes.")
    payload = json.dumps({"command":"water", "zone": watering_zone, "duration": watering_minutes})

    print(f"Publishing {payload} to topic {topic}")
    # Change topic, qos and payload
    response = client.publish(
        topic=topic,
        qos=1,
        payload=payload
    )
    
    print(f"Published {payload} to topic {topic}")

    
    return {
        'statusCode': 200,
        'body': json.dumps('Successfully received.  Please see topic for instruction.')
    }
