#!/usr/bin/python3
# Ensures that the RGB-CCT lights have turned off, via Zigbee2MQTT

from helpers import *

# What lights to control
lights = ["Floor0/Dining/LightLeft","Floor0/Dining/LightRight"]
# Should we report what we're doing?
set_verbose(False)

# MQTT details
mqtt_server = "127.0.0.1"
mqtt_port = 1883

# Connect to the MQTT server
connect(mqtt_server, mqtt_port)

# Make sure the lights are off
all_lights_off(lights)

# Wait for that to go through before disconnecting
time.sleep(2)
