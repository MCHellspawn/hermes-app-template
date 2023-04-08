#!/bin/bash

SKILLNAME=""
# Absolute path to this script, e.g. /home/user/bin/foo.sh
SCRIPT=$(readlink -f "$0")
# Absolute path this script is in, thus /home/user/bin
SCRIPTPATH=$(dirname "$SCRIPT")
USER=$(who)
read -p "Enter MQTT Hostname: " MQTT_HOST
read -p "Enter MQTT Port:" -i "1833" MQTT_PORT
read -p "Enter MQTT User:" MQTT_USER
read -p "Enter MQTT Password:" MQTT_PASS
echo $SCRIPTPATH

# Create the app path and move the files
mkdir -p /usr/lib/rhasspy-skills/app-$SKILLNAME
cp -r $SCRIPTPATH/* /usr/lib/rhasspy-skills/app-$SKILLNAME
cd /usr/lib/rhasspy-skills/app-$SKILLNAME

# Create and activate the python virtual environment
python3 -m venv app-$SKILLNAME
source app-$SKILLNAME/bin/activate

# Install dependancies in virtual environment
pip3 install -r requirements.txt

# Deactivate the pyton virtual environment
deactivate

# Remove existing service definition
sudo rm -f /lib/systemd/system/rhasspy.skill.$SKILLNAME.service

# Create new service definition
touch /lib/systemd/system/rhasspy.skill.$SKILLNAME.service
:> /lib/systemd/system/rhasspy.skill.$SKILLNAME.service

echo "
[Unit]
Description=Rhasspy $SKILLNAME Skill
After=multi-user.target

[Service]
Type=simple
User=$USER
ExecStart=/bin/bash -c 'cd /usr/lib/rhasspy-skills/app-$SCRIPTPATH && source app-$SCRIPTPATH/bin/activate && python3 hermes-app.py --host "$MQTT_HOST" --username "$MQTT_USER" --password "$MQTT_PASS" --port "$MQTT_PORT"'
Restart=on-abort

[Install]
WantedBy=multi-user.target

  " >>  /lib/systemd/system/rhasspy.skill.$SKILLNAME.service

sudo sudo chmod 644 /lib/systemd/system/rhasspy.skill.$SKILLNAME.service
sudo systemctl stop rhasspy.skill.$SKILLNAME.service
sudo systemctl daemon-reload
sudo systemctl enable rhasspy.skill.$SKILLNAME.service
sudo systemctl start rhasspy.skill.$SKILLNAME.service
#sudo reboot