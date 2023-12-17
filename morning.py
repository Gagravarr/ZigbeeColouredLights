#!/usr/bin/python3
# Make the RGB-CCT LED strips in the window fake it being nice
#  and bright outside in the morning, with a believable
#  white light, over a few hours. Via Zigbee2MQTT
# https://www.zigbee2mqtt.io/devices/ZB-RGBCW.html#light

import signal, time
import numpy, math
from helpers import *

# What lights to control? 
lights = ("Floor0/Dining/LightLeft","Floor0/Dining/LightRight")
##lights = ("Floor0/Dining/Lights")
# What colour temperatures to move between?
colour_temp_range = (500,200)
# What brightnesses to move between?
brightness_range = (20,200)
# How long to spend "waking up"
wakeup_seconds = 80 * 60
# How long to switch off over
finish_seconds = 10 * 60
# Minimum gap between changes
minimum_pause = 15

# Should we report what we're doing?
verbose = set_verbose(True)

# MQTT details
mqtt_server = "127.0.0.1"
mqtt_port = 1883

# Connect to the MQTT server
client = connect(mqtt_server, mqtt_port)


# How many transitions to have, and how long?
wakeup_changes = min(20, math.ceil(wakeup_seconds/minimum_pause))
finish_changes = min(10, math.ceil(finish_seconds/minimum_pause))
wakeup_pause = wakeup_seconds/wakeup_changes
finish_pause = finish_seconds/finish_changes

# Calculate the transitions
wakeups = zip(
   numpy.linspace(colour_temp_range[0],colour_temp_range[1],wakeup_changes,dtype="int"),
   numpy.linspace(brightness_range[0],brightness_range[1],wakeup_changes,dtype="int")
)
finishes = zip(
   numpy.full((finish_changes),colour_temp_range[1],dtype="int"),
   numpy.linspace(brightness_range[1],brightness_range[0],finish_changes,dtype="int")
)

# Builds the JSON for a state
def as_json(temp, bright):
   return {"color_temp":"%d"%temp, "brightness":"%d"%bright}

# Initialise the lights to the initial state, before switching on
# TODO

# Make sure the lights are on, and ready
# TODO Set them to the initial before turning on
all_lights_on(lights)
time.sleep(0.5)

# Switch lights off on exit
shutdown = make_shutdown_signal_handler(lights)
signal.signal(signal.SIGINT, shutdown)

# Do the wakeup, then the finish
for stage,pause,data in (
        ("Wakeup",wakeup_pause,wakeups),("Finish",finish_pause,finishes)):
  if verbose:
     print("%s - pause %1.1f" % (stage,pause))
  for temp, bright in data:
     if verbose:
        print(" * Colour Temperature %d, Brightness %d" % (temp, bright))
     message = as_json(temp,bright)
     send_all(lights, message)
     time.sleep(pause)

# Turn off lights and finish
shutdown(None,None)
