# Helpers for things we often want to do, such as
#  - Pick a Random Colour
#  - Generate a Range of Colour Temperatures and Brightness
#  - Sent to multiple devices
#
# For RGB-CCT LED strips
# https://www.zigbee2mqtt.io/devices/ZB-RGBCW.html#light

import paho.mqtt.client as mqtt
import random, json, time
import colorsys, sys

_base_topic = "zigbee2mqtt"
_verbose = False
_client = None

def set_base_topic(topic):
   _base_topic = topic
def set_verbose(verbose=True):
   _verbose = verbose

def connect(mqtt_server, mqtt_port):
   global _client
   _client = mqtt.Client()
   _client.connect(mqtt_server, mqtt_port, 60)
   return _client


# Send the same message to each light's topic (or group topic)
# Allows a small pause between each light, to try to avoid
#  occassional "sendZclFrameToEndpointInternal error"
def send_all(lights, message):
   if isinstance(message, dict):
      message = json.dumps(message)
   for light in lights:
      topic = "%s/%s/set" % (_base_topic, light)
      _client.publish(topic, payload=message)
      time.sleep(0.05)

def all_lights_on(lights):
   send_all(lights, {"state":"on"})

def all_lights_off(lights):
   send_all(lights, {"state":"off"})

# Switch lights off on exit
def make_shutdown_signal_handler(lights):
   def shutdown_signal_handler(sig, frame):
      print('Shutting down...  ', end='')
      all_lights_off(lights)
      time.sleep(2)
      _client.disconnect()
      print('... Shutdown complete')
      sys.exit(0)
   return shutdown_signal_handler


last_h = 0.0
def random_colour(min_change=0.0):
   # Pick a "random" HSV colour
   # H needs to change by the minimum amount
   # Prefer a high V for more brigh colours
   # Prefer a high S for less white
   global last_h
   h = (last_h + random.uniform(min_change, 1-min_change)) % 1.0
   s = random.uniform(0.5, 1.0)
   v = random.uniform(0.5, 1.0)
   rgb = colorsys.hsv_to_rgb(h, s, v)
   last_h = h
   return [int(c*255) for c in rgb]

def random_hex_colour(min_change=0.0):
  rgb = random_colour(min_change)
  if _verbose:
     print("".join('{:02X}'.format(v) for v in rgb))
  nc = {"r":rgb[0], "g":rgb[1], "b":rgb[2]}
  return nc
