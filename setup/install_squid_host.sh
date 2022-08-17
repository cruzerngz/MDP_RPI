#!/bin/bash

SCRIPT_PATH=$(cd $(dirname $0); pwd)

source $SCRIPT_PATH/functions.sh ## some helpers
source $SCRIPT_PATH/echo_colours.sh

echo_bold_green "This script should be run on your HOST computer."


sudo apt install -y squid
remove_partial_matching_line "http_access deny all" /etc/squid/squid.conf
append_if_missing "http_access allow all" /etc/squid/squid.conf


