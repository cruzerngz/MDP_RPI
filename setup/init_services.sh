#!/bin/bash

SCRIPT_PATH=$(cd $(dirname $0); pwd)

source $SCRIPT_PATH/echo_colours.sh
source $SCRIPT_PATH/functions.sh

echo_bold_red "This script will disable ALL wireless connections!"
echo_red "Use a tethered network connection (usb0) for networking"

sudo killall wpa_supplicant
sudo systemctl disable wpa_supplicant

sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl enable dnsmasq
sudo systemctl enable bluetooth
sudo systemctl daemon-reload

# sudo systemctl start hostapd
# sudo systemctl start dnsmasq
# sudo systemctl start
sudo service hostapd restart
sudo service dnsmasq restart
sudo service bluetooth restart



