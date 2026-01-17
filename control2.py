#!/usr/bin/python3
# Uses a Zigbee button to cycle the CCT lights on / off /
#  temperature, via Zigbee2MQTT
# Note that this would probably be easier with HomeAssistant...

import signal, sys
from enum import Enum
from helpers import *

# What lights to control
lights = ["Floor3/Lounge/LightBookshelf"]
# What button to watch
button = "Floor3/Lounge/SwitchBookshelf"
# Should we report what we're doing?
verbose = set_verbose(True)
# How long to listen for, unless specified as an argument
run_seconds = time_arguments([60*60])
stop_at = time.time() + run_seconds

# What colour temperatures to move between?
colour_temp_range = (153,500)
# What brightness to use
brightness = 254
# How long to spend changing
transition = default_transition = 4

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
LightState = Enum("LightState", ["Off","White"])
state = LightState.Off

# Moves to the next state, handling on/off as needed
def next_state():
  global state, transition

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
  global state, transition

  # What was the button action?
  action = msg.get("action", None)

  # Single or Double press?
  double = (action == "double")

  # Ignore 'on', everything is single / double
  if action == "on":
    return

  # To change state, Double or be Off
  if state == LightState.Off or double:
    next_state()

  # Change to the next setting of the current/new state
  if state == LightState.Off:
    return
  if state == LightState.White:
    temp, bright = random_temperature_brightness(colour_temp_range, [brightness,brightness])
    settings = {"color_temp":"%d"%temp, "brightness":"%d"%bright}
    if verbose:
      print("Picking Colour Temperature %d, Brightness %d" % (temp,bright))
    send_all(lights, settings)

# Listen to the button
receive(button, button_pressed)
print("Now waiting...")

# Run until the limit, changing as needed
client.loop_start()
while time.time() < stop_at:
  time.sleep(2)

# Finish by turning off
all_lights_off(lights)
