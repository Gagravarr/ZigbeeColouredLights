#!/usr/bin/python3
# Uses a Zigbee button to cycle the RGB-CCT lights through various
#  different modes, via Zigbee2MQTT
# Note that this would probably be easier with HomeAssistant...

import signal
from helpers import *

# What lights to control
lights = ["Floor0/Dining/LightLeft","Floor0/Dining/LightRight"]
# What button to watch
button = "Floor0/Dining/SwitchLight"
# Should we report what we're doing?
set_verbose(True)
##set_verbose(False)

# MQTT details
mqtt_server = "127.0.0.1"
mqtt_port = 1883

# Connect to the MQTT server
client = connect(mqtt_server, mqtt_port)

# Handles button presses
def todo_button(msg):
  print("Got one!")
  print(msg)

# Listen to the button
receive(button, todo_button)
print("Now waiting...")

# Begin with all lights off
all_lights_off(lights)

# TODO Wait until we switch off
client.loop_start()
time.sleep(20)
