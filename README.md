# Rhasspy Template Skill (Rhasspy_App_Template)

A template for a skill for [Rhasspy](https://github.com/rhasspy). This skill is implemented as a Hermes app and uses the [Rhasspy-hermes-app](https://github.com/rhasspy/rhasspy-hermes-app) library. The script can be run as a service, or as a docker container (recommended). 

## Installing

Requires:
* rhasspy-hermes-app 1.1.2

### In Docker:
To install, clone the repository and execute docker build to build the image.

```bash
sudo docker build hermes-app-template -t <image_name>
```

### In Rhasspy:
Setup the slot program:
1. SSH into the Rhasspy device 
   * If using a base/satellite setup this is typically done on the base
2. Navigate to your slot programs folder
   * for example "/profiles/en/slot_programs"
```bash
cd /profiles/en/slot_programs
```
3. Create a folder name "template" and navigate to it
```bash
mkdir template
cd template
```
4. Download the slot program from the github repo
```bash
```
5. Setup the slot variables
```ini
```
6. Use the slot variables in a sentence
```ini
```

## Configuration

Edit the setup section with the connection settings for Grocy and Rhasspy:
```ini
[Rhasspy]
# May be http or https
protocol = http
# Hostname or IP for Rhasspy intent recognition device
host = rhasspybase.local
# Port for Rhasspy device used above
port = 12101
```

* Rhasspy
  * `protocol: string` - http or https
  * `host: string` - URL of the Rhasspy device handling intent recognition
  * `port: integer` - IP Port of the Rhasspy device handling intent recognition

## Using

Build a docker container using the image created above.
Bind the config volume <path/on/host>:/app/config

```bash
sudo docker run -it -d \
        --restart always \
        --name <container_name> \
        -v <path/on/host>:/app/config \
        -e "MQTT_HOST=<MQTT Host/IP>" \
        -e "MQTT_PORT=<MQTT Port (Typically:1883)" \
        -e "MQTT_USER=<MQTT User>" \
        -e "MQTT_PASSWORD=<MQTT Password>" \
        <image_name>
```

The following intents are implemented on the hermes MQTT topic:

```ini
[Intent1]

```

## To-Do

* 