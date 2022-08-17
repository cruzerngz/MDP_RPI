#!/bin/bash
# This script installs all prerequisites/dependencies
# (as specified in the RPi technical materials)

SCRIPT_PATH=$(cd $(dirname $0); pwd)

source $SCRIPT_PATH/functions.sh ## some helpers
source $SCRIPT_PATH/echo_colours.sh

set -e

WLAN_IP="192.168.12"

# echo_red "disabling wpa_supplicant"
# sudo systemctl disable wpa_supplicant
# sudo service wpa_supplicant stop

echo_green "performing raspi-configs"
sudo raspi-config nonint do_boot_behaviour B2
# sudo raspi-config nonint get_camera
sudo raspi-config nonint do_camera 1
# $RPI_CFG_PREFIX --expand-rootfs


echo_green "Enabling camera"
sudo sed -i "s/start_x=0/start_x=1/g" /boot/config.txt

echo_green "Setting timezone"
sudo timedatectl set-timezone Asia/Singapore

echo_green "Purging unnecessary packages"
sudo apt purge wolfram-engine libreoffice*

echo_green "updating system packages..."
sudo apt update
# sudo apt update && sudo apt upgrade -y

echo_green "Installing dependencies"
sudo apt install -y \
hostapd \
dnsmasq \
netfilter-persistent \
iptables-persistent \
apache2 \
samba \
samba-common-bin

echo_green "Installing version-specific dependencies"
# sudo apt install -y iptables=1.6
sudo apt-mark hold iptables ## keep iptables at v1.6


HOSTAPD_CONF=(
    "interface=wlan0"
    "driver=nl80211"
    "ssid=MDPGrp12"
    "wpa_passphrase=2022mdp12"
    "hw_mode=g"
    "channel=11" # channel 0 causes issues with auto channel selection, do not use!
    "macaddr_acl=0"
    "auth_algs=1"
    "ignore_broadcast_ssid=0"
    "wpa=2"
    "wpa_key_mgmt=WPA-PSK"
    "rsn_pairwise=CCMP"
    "ieee80211n=1"
    "wmm_enabled=1"
)

HOSTAPD_DAEMON_LINE='DAEMON_CONF="/etc/hostapd/hostapd.conf"'

echo_green "configuring hostapd"

for hostapdline in "${HOSTAPD_CONF[@]}"
do
    append_if_missing "$hostapdline" /tmp/hostapd.conf
done
# cat $HOSTAPD_CONF >> /tmp/hostapd.conf #/etc/hostapd/hostapd.conf
sudo mv /tmp/hostapd.conf /etc/hostapd/hostapd.conf

append_if_missing $HOSTAPD_DAEMON_LINE /etc/default/hostapd

# echo_green "enabling hostapd"
# sudo /usr/sbin/hostapd /etc/hostapd/hostapd.conf
# sudo systemctl unmask hostapd
# sudo systemctl enable hostapd
# sudo systemctl start hostapd

echo_green "setting up wlan0"
# WLAN_CONF="interface wlan0\n\
# static ip_address=$WLAN_IP.1\24\n\
# nohook wpa_supplicant"
# sudo append_if_missing $WLAN_CONF /etc/dhcpcd.conf
append_if_missing "interface=wlan0" /etc/dhcpcd.conf
append_if_missing "static ip_address=$WLAN_IP.1\24" /etc/dhcpcd.conf
append_if_missing "nohook wpa_supplicant" /etc/dhcpcd.conf

echo_green "setting up DHCP server"
DHCP_START="$WLAN_IP.2"
DHCP_END="$WLAN_IP.100"
DHCP_SUBNET_MASK="255.255.255.0"

# DHCP_CONF="interface=wlan0\n\
# dhcp-range=$DHCP_START,$DHCP_END,$DHCP_SUBNET_MASK,24H"
# sudo append_if_missing $DHCP_CONF /etc/dnsmasq.conf
append_if_missing "interface=wlan0" /etc/dnsmasq.conf
append_if_missing "dhcp-range=$DHCP_START,$DHCP_END,$DHCP_SUBNET_MASK,24H" /etc/dnsmasq.conf
# sudo systemctl start dnsmasq

echo_green "setting up eth0 IP forwarding"
sudo sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"
remove_partial_matching_line "net.ipv4.ip_forward" /etc/sysctl.conf
append_if_missing "net.ipv4.ip_forward=1" /etc/sysctl.conf

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
echo_bold_green "perform a reboot and continue with install_config-2.sh through a tethered connection."
