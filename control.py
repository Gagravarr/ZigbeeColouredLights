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

# MQTT details
mqtt_server = "127.0.0.1"
mqtt_port = 1883

# Connect to the MQTT server
client = connect(mqtt_server, mqtt_port)

# Switch lights off on exit
signal.signal(signal.SIGINT, make_shutdown_signal_handler(lights))

# Begin with all lights off
all_lights_off(lights)

# The current state
LightState = Enum("LightState", ["Off","White","Colour","Changing"])
state = LightState.Off

# Moves to the next state, with wraparound to Off
def next_state():
  global state
  ns = state.value + 1
  if ns in LightState:
    state = LightState(ns)
  else:
    state = LightState.Off

# Handles button presses
def button_pressed(msg):
  global state

  # Single or Double press?
  double = msg.get("action",None) == "double"

  # If it's off, anything means turn on
  if state == LightState.Off:
    if verbose:
      print("Turning the lights on")
    all_lights_on(lights)
    next_state()
    return

  # If it's double, move to the next state
  if double:
    next_state()

    if state == LightState.Off:
      if verbose:
        print("Turning the lights off")
      state = LightState.Off.value
      all_lights_off(lights)
      return
    if verbose:
      print("Lights state changed to %s" % state.name)

  # Change to the next setting of the current/new state
  # TODO

# Listen to the button
receive(button, button_pressed)
print("Now waiting...")


# TODO Check the arguments to see how long to listen for
client.loop_start()
time.sleep(run_minutes * 60)
# TODO support changing
