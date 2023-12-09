#!/usr/bin/python3
# Random slowly changing light colours, via Zigbee2MQTT
# For RGB-CCT LED strips
# https://www.zigbee2mqtt.io/devices/ZB-RGBCW.html#light

import paho.mqtt.client as mqtt
import random, time, json
import signal, sys
import colorsys

# What lights to control
lights = ["Floor0/Dining/LightLeft","Floor0/Dining/LightRight"]
# How long to spend changing each colour
transition = 4
# How long between colour changes (needs to include transition!)
change_every = transition*2
# Should we report what colour we're picking next?
verbose = False

# MQTT details
base_topic = "zigbee2mqtt"
mqtt_server = "127.0.0.1"
mqtt_port = 1883

# Connect to the MQTT server
client = mqtt.Client()
client.connect(mqtt_server, mqtt_port, 60)

# Send the same message to each light's topic
def send_all(message):
   if isinstance(message, dict):
      message = json.dumps(message)
   for light in lights:
      topic = "%s/%s/set" % (base_topic, light)
      client.publish(topic, payload=message)

def random_colour():
   # Pick a random HSV colour
   # Prefer a high V for more brigh colours
   # Prefer a high S for less white
   h = random.random()
   s = random.uniform(0.5, 1.0)
   v = random.uniform(0.5, 1.0)
   rgb = colorsys.hsv_to_rgb(h, s, v)
   return [int(c*255) for c in rgb]

# Make sure the lights are on
send_all({"state":"on"})

# Switch lights off on exit
def signal_handler(sig, frame):
   print('Shutting down')
   send_all({"state":"off"})
   client.disconnect()
   sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# Keep picking new colours between pauses
while True:
  rgb = random_colour()
  if verbose:
     print("".join('{:02X}'.format(v) for v in rgb))
  nc = {"r":rgb[0], "g":rgb[1], "b":rgb[2]}
  send_all({"color":nc, "transition":transition})
  time.sleep(change_every)
