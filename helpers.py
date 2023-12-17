# Helpers for things we often want to do, such as
#  - Pick a Random Colour
#  - Generate a Range of Colour Temperatures and Brightness
#  - Sent to multiple devices
#
# For RGB-CCT LED strips
# https://www.zigbee2mqtt.io/devices/ZB-RGBCW.html#light

import random, json, time
import colorsys

_base_topic = "zigbee2mqtt"
_verbose = False

def set_base_topic(topic):
   _base_topic = topic
def set_verbose(verbose=True):
   _verbose = verbose


# Send the same message to each light's topic (or group topic)
# Allows a small pause between each light, to try to avoid
#  occassional "sendZclFrameToEndpointInternal error"
def send_all(client, light_topics, message):
   if isinstance(message, dict):
      message = json.dumps(message)
   for light in lights:
      topic = "%s/%s/set" % (_base_topic, light)
      client.publish(topic, payload=message)
      time.sleep(0.05)

def all_lights_on():
   send_all({"state":"on"})

def all_lights_off():
   send_all({"state":"off"})

# Switch lights off on exit
def shutdown_signal_handler(sig, frame):
   print('Shutting down...  ', end='')
   all_lights_off()
   time.sleep(2)
   client.disconnect()
   print('... Shutdown complete')
   sys.exit(0)


last_h = 0.0
def random_colour():
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

def random_hex_colour():
  rgb = random_colour()
  if _verbose:
     print("".join('{:02X}'.format(v) for v in rgb))
  nc = {"r":rgb[0], "g":rgb[1], "b":rgb[2]}
  return nc
