#. /home/pi/venvs/iot/bin/activate
. /home/pi/venvs/iot39/bin/activate
#python ~/iot/aws-iot-device-sdk-python-v2/samples/pubsub.py --topic test/chat --root-ca /home/pi/iot/certs/greenhouse-sensor-z2-AmazonRootCA1.pem  --key /home/pi/iot/certs/greenhouse-sensor-z2-private.pem.key --cert /home/pi/iot/certs/greenhouse-sensor-z2-device.pem.crt --endpoint a1n6fj3nzgfi04-ats.iot.us-east-1.amazonaws.com
ROOT_CA=/home/pi/iot/certs/greenhouse-sensor-z2-AmazonRootCA1.pem
KEY=/home/pi/iot/certs/greenhouse-sensor-z2-private.pem.key
CERT=/home/pi/iot/certs/greenhouse-sensor-z2-device.pem.crt
ENDPOINT=a1n6fj3nzgfi04-ats.iot.us-east-1.amazonaws.com
nohup python ./driver.py --topic greenhouse/metrics --root-ca ${ROOT_CA} --key ${KEY} --cert ${CERT} --endpoint ${ENDPOINT} | tee output.log &
