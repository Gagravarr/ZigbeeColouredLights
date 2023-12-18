#!/usr/bin/python3
# Make the RGB-CCT LED strips in the window fake it being nice
#  and bright outside in the morning, with a believable
#  white light, over a few hours. Via Zigbee2MQTT
# https://www.zigbee2mqtt.io/devices/ZB-RGBCW.html#light

import signal, time
import numpy, math
from collections import namedtuple
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


# Builds up the JSON and pauses for everything
spds = []
SPD = namedtuple("SPD",["stage","pause","data","summary"])
for stage,pause,data in (
        ("Wakeup",wakeup_pause,wakeups),("Finish",finish_pause,finishes)):
   for temp, bright in data:
      setting = {"color_temp":"%d"%temp, "brightness":"%d"%bright}
      summary = "Colour Temperature %d, Brightness %d" % (temp, bright)
      spds.append(SPD(stage,pause,setting,summary))


# Initialise the lights to the initial state, before switching on
send_all(lights, spds[0].data)

# Make sure the lights are on, and ready
all_lights_on(lights)
time.sleep(0.5)

# Switch lights off on exit
shutdown = make_shutdown_signal_handler(lights)
signal.signal(signal.SIGINT, shutdown)

# Move through all the stages
for spd in spds:
  if verbose:
     print("%s (%d secs) - %s" % (spd.stage,spd.pause,spd.summary))
  send_all(lights, spd.data)
  time.sleep(spd.pause)

# Turn off lights and finish
all_lights_off(lights)
time.sleep(5)
