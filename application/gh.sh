#. /home/pi/venvs/iot/bin/activate
. /home/pi/venvs/iot39/bin/activate
nohup python ./driver.py --topic greenhouse/metrics | tee /home/pi/iot/logs/output.log &
