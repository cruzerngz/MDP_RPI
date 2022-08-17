#!/bin/bash

SCRIPT_PATH=$(cd $(dirname $0); pwd)
SCRIPT_NAME=$(basename $0)

case $# in
    0)
        echo "Tunnel to a device"
        echo "Param 1: username"
        echo "Param 2: ip address"
        echo "Param 3++: (optional) additional flags to pass"
        ;;
    1)
        echo "Invalid"
        bash $SCRIPT_PATH/$SCRIPT_NAME
        ;;
    *)
        ssh -R 3129:localhost:3128 "$1@$2" "${@:3}"
esac


ssh -R 3129:localhost:3128 user@HostB