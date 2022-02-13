# greenhouse-iot
## General Pi Setup
Enable I2C - go through the Preferences - Interfaces UI
Enable SSH - go through the Preferences - Interfaces UI
Make sure WIFI is setup in /etc/wpa_supplicant/wpa_supplicant.conf
Static IP - Eero Settings - Network Settings - Reservations & port forwarding -- set a static IP for the device.  Verify with ifconfig -a.

## Libraries for I2C and IoT
sudo apt-get update
sudo apt-get install i2c-tools

### Note:  This page has setup from AWS with additional steps
https://docs.aws.amazon.com/iot/latest/developerguide/connecting-to-existing-device.html

## Install through this tutorial https://docs.aws.amazon.com/iot/latest/developerguide/iot-quick-start.html
installed Linux Python IoT SDK to 
pi@raspberrypi:/iot

And successfully ran the ./start.sh to validate communication.

