# Pi setup
There are 2 setup stages:
- Flashing the boot image to a micro SD card
- Installing all software dependencies

## MicroSD card setup
[Raspberry Pi Imager](https://github.com/raspberrypi/rpi-imager) is used to flash the micro SD card.

The following advanced options are used:

| Setting         | Value                         |
|-----------------|-------------------------------|
| OS              | Pi OS lite 32-bit             |
| SSH             | enabled, pub key auth         |
| Authorized key  | **your public key**           |
| Hostname        | mdp12                         |
| Username        | pi3                           |
| Password        | mdp                           |
| Wireless LAN    | **off. set locale on boot**   |
<!-- | WLAN passoword  | *your network password*       | -->
| Time zone       | Asia/Singapore                |
| Keyboard layout | US                            |

Networking to the Pi is done through a usb tether.
SSH authenticaion is key-based only.

Once the image is flashed, install into the Pi and reboot.
The Pi should boot and connect automatically to the SSID specified.
Search for the Pi's IP address and login using:

`ssh pi3@<local ip>`

## Get the script
After first boot, clone this repo by running:

`git clone https://github.com/cruzerngz/MDP_RPI.git`

Scripts are found in `$REPOPATH/setup`

## Install dependencies
Run `sudo bash install.sh` to install and configure the rest of the settings.

Some configuration files need to be edited manually.

In `/etc/systemd/system/dbus-org.bluez.service`:
- Add `-C --noplugin=sap` to the end of `ExecStart=`
- Add `ExecStartPost=/usr/bin/sdptool add SP` directly under the `ExecStart` line

Run `bluetoothctl` and do the following:
```
discoverable on
agent on
default-agent
exit
```



