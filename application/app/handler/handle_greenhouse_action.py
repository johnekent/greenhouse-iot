import json
import boto3

def lambda_handler(event, context):
    print(f"Receieved event {event} with context {context}")

    location = event['location']
    volume_gallons = event['volume_gallons']

    print(f"The location of event is {location} and the volume is {volume_gallons}")

    client = boto3.client('iot-data', region_name='us-east-1')
    print(f"Created iot-data client {client}")

    topic = "greenhouse/command"

    gal = float(volume_gallons)

    if isinstance(gal, float):
        # jibberish math
        duration = 1000 - 17.3 * gal
    else:
        print(f"The parameter {volume_gallons} wasn't convertible to float so choosing 1")
        duration = 1

    payload = json.dumps({"command":"flush", "duration": duration})

    print(f"Publishing {payload} to topic {topic}")
    # Change topic, qos and payload
    response = client.publish(
        topic=topic,
        qos=1,
        payload=payload
    )

    print(f"Published {payload} to topic {topic}")
