#!/usr/bin/python3
# Random slowly changing light colours, via Zigbee2MQTT
# For RGB-CCT LED strips
# https://www.zigbee2mqtt.io/devices/ZB-RGBCW.html#light
#
# TODO Support a button to turn off/exit

import signal
from helpers import *

# What lights to control
lights = ["Floor0/Dining/LightLeft","Floor0/Dining/LightRight"]
# What is the minimum change in colour each time?
min_change = 0.2
# How long to spend changing each colour
transition = 5
# How long between colour changes (needs to include transition!)
change_every = transition*2
# Should we report what colour we're picking next?
set_verbose(False)

# MQTT details
mqtt_server = "127.0.0.1"
mqtt_port = 1883

# Connect to the MQTT server
connect(mqtt_server, mqtt_port)

# Make sure the lights are on
all_lights_on(lights)

# Switch lights off on exit
signal.signal(signal.SIGINT, make_shutdown_signal_handler(lights))

# Keep picking new colours between pauses
while True:
  nc = random_hex_colour(min_change=min_change)
  send_all(lights, {"color":nc, "transition":transition})
  time.sleep(change_every)
