#!/bin/bash

SCRIPT_PATH=$(cd $(dirname $0); pwd)

source $SCRIPT_PATH/echo_colours.sh
source $SCRIPT_PATH/functions.sh

echo_green "setting up NAT" ## requires a reboot here
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"
sudo netfilter-persistent save

echo_green "setting up bluetooth"
append_if_missing "PRETTY_HOSTNAME=MDP-TEAM-12" /etc/machine-info


# automoate bluetooth conn
remove_partial_matching_line "exit 0" /etc/rc.local
append_if_missing "sudo rfcomm watch hci0" /etc/rc.local
append_if_missing "exit 0" /etc/rc.local

echo_green "setting up SSH tunneling"
append_if_missing "export http_proxy=http://127.0.0.1:3129" /etc/environment
append_if_missing "export https_proxy=http://127.0.0.1:3129" /etc/environment
source /etc/environment

echo_bold_green "done"