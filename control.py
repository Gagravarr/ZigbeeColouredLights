#!/usr/bin/python3
# Uses a Zigbee button to cycle the RGB-CCT lights through various
#  different modes, via Zigbee2MQTT
# Note that this would probably be easier with HomeAssistant...

import signal, sys
from enum import Enum
from helpers import *

# What lights to control
lights = ["Floor0/Dining/LightLeft","Floor0/Dining/LightRight"]
# What button to watch
button = "Floor0/Dining/SwitchLight"
# Should we report what we're doing?
verbose = set_verbose(True)
# How long to listen for, unless specified as an argument
run_minutes = 60

# What colour temperatures to move between?
colour_temp_range = (200,500)
# What brightnesses to move between?
brightness_range = (20,200)
# How long to spend changing
transition = 8

# MQTT details
mqtt_server = "127.0.0.1"
mqtt_port = 1883

# Connect to the MQTT server
client = connect(mqtt_server, mqtt_port)

# Switch lights off on exit
signal.signal(signal.SIGINT, make_shutdown_signal_handler(lights))

# Begin with all lights off
all_lights_off(lights)
# TODO Support going to a specific initial state other than off

# The current state
LightState = Enum("LightState", ["Off","White","Colour","Changing"])
state = LightState.Off

# Moves to the next state, handling on/off as needed
def next_state():
  global state

  nsv = state.value + 1
  nextstate = LightState(nsv) if (nsv in LightState) else list(LightState)[0]
  if verbose:
    print("Lights state changing from %s to %s" % (state.name, nextstate.name))

  if state == LightState.Off:
    all_lights_on(lights)
  if nextstate == LightState.Off:
    all_lights_off(lights)
  state = nextstate

# Handles button presses
def button_pressed(msg):
  global state

  # Single or Double press?
  double = msg.get("action",None) == "double"

  # To change state, Double or be Off
  if state == LightState.Off or double:
    next_state()

  # Change to the next setting of the current/new state
  if state == LightState.Off:
    return
  if state == LightState.White:
    temp, bright = random_temperature_brightness(colour_temp_range, brightness_range)
    settings = {"color_temp":"%d"%temp, "brightness":"%d"%bright}
    if verbose:
      print("Picking Colour Temperature %d, Brightness %d" % (temp,bright))
    send_all(lights, settings)
  else:
    pick_random_colour()

def pick_random_colour():
  temp, bright = random_temperature_brightness(colour_temp_range, brightness_range)
  nc = random_hex_colour(min_change=0.1)
  settings = {"color":nc, "brightness":"%d"%bright}
  if state == LightState.Changing:
    settings["transition"] = transition
  if verbose:
    print("Picking Colour %s, Brightness %d" % (nc,bright))
  send_all(lights, settings)

# Listen to the button
receive(button, button_pressed)
print("Now waiting...")


# TODO Check the arguments to see how long to listen for
client.loop_start()
time.sleep(run_minutes * 60)
# TODO support changing

# Finish by turning off
all_lights_off(lights)
