#!/usr/bin/python3
# Make the RGB-CCT LED strips in the window fake it being nice
#  and bright outside in the morning, with a believable
#  white light, over a few hours. Via Zigbee2MQTT
# https://www.zigbee2mqtt.io/devices/ZB-RGBCW.html#light

import random, json, math, time
import signal, sys
import numpy
from helpers import send_all as _send_all, connect

# What lights to control? 
##lights = ("Floor0/Dining/LightLeft","Floor0/Dining/LightRight")
lights = ("Floor0/Dining/Lights")
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
verbose = True

# MQTT details
base_topic = "zigbee2mqtt"
mqtt_server = "127.0.0.1"
mqtt_port = 1883

# Connect to the MQTT server
client = connect(mqtt_server, mqtt_port)

# Send the same message to each light's topic
def send_all(message):
   _send_all(lights, message)


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

# Make sure the lights are on, and ready
send_all({"state":"on"})
time.sleep(0.5)

# Switch lights off on exit
def signal_handler(sig, frame):
   print('Shutting down')
   send_all({"state":"off"})
   client.disconnect()
   sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# Do the wakeup, then the finish
for stage,pause,data in (
        ("Wakeup",wakeup_pause,wakeups),("Finish",finish_pause,finishes)):
  if verbose:
     print("%s - pause %1.1f" % (stage,pause))
  for temp, bright in data:
     if verbose:
        print(" * Colour Temperature %d, Brightness %d" % (temp, bright))
     send_all( as_json(temp,bright) )
     time.sleep(pause)

# Shutdown
signal_handler(None,None)
