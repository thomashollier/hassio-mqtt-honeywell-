#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import subprocess
import json
import logging

# need to use logging instead of print since we are running as a service
logging.basicConfig(level="INFO")
logging.info("starting climate2mqtt")

gmode = "0"

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flag, rc):
    logging.info("Connected")
    logging.info("Connected with result code %s" % (str(rc)))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("hvac/central/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    logging.info("Received message:")
    logging.info("Topic: %s" % str(msg.topic))
    logging.info("Message: %s" % str(msg.payload))
    {
        "hvac/central/temperature/set": set_temperature,
        "hvac/central/mode/set": set_mode,
        "hvac/central/fan/set": set_fan,
	"hvac/central/status": get_status,
    }.get(str(msg.topic), wrong_topic)(client, msg)

def wrong_topic(client, msg):
    logging.info(str(msg.topic))

def set_temperature(client, msg):
    logging.info("Executing: set_temperature()")
    logging.info("Running command: gmode is: %s" % str(gmode))
    client.publish("hvac/central/temperature/state", str(msg.payload.decode("utf-8")))
    cmd = "python3 /usr/share/hassio/homeassistant/scripts/totalcomfort.py -h %s" % str(msg.payload.decode("utf-8"))
    if (gmode == "3"): #cool mode
        cmd = "python3 /usr/share/hassio/homeassistant/scripts/totalcomfort.py -c %s" % str(msg.payload.decode("utf-8"))
    logging.info(str("Running command: %s" % cmd))
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    result = out.split('\n')
    for lin in result:
        if not lin.startswith('#'):
            logging.info(lin)

def get_status(client, msg):
    logging.info("Executing: get_status()")
    cmd = "python3 /usr/share/hassio/homeassistant/scripts/totalcomfort.py -j"
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    result = out.split('\n')
    for lin in result:
        if not lin.startswith('#'):
             logging.info(lin)
    j = json.loads(result[0])

    client.publish("hvac/central/temperature/current", j['latestData']['uiData']["DispTemperature"])
    client.publish("hvac/central/temperature/state", j['latestData']['uiData']["HeatSetpoint"])

    fan_state = ("auto") if (j['latestData']['fanData']["fanMode"] == "0") else "always_on"
    client.publish("hvac/central/fan/state", fan_state)

    global gmode
    mode = "stop"
    gmode = j['latestData']['uiData']["SystemSwitchPosition"]
    if (gmode == 0):
        mode = "emheat"
    if (gmode == 1):
        mode = "heat"
    if (gmode == 2):
        mode = "cool"
    client.publish("hvac/central/mode/state", mode)

def set_mode(client, msg):
    logging.info("Executing: set_mode()")
    client.publish("hvac/central/mode/state", str(msg.payload.decode("utf-8")))
    mode = "2"
    if (str(msg.payload.decode("utf-8")).startswith('emheat')):
        mode = "0"
    if (str(msg.payload.decode("utf-8")).startswith('heat')):
        mode = "1"
    if (str(msg.payload.decode("utf-8")).startswith('cool')):
        mode = "3"
    cmd = "python3 /usr/share/hassio/homeassistant/scripts/totalcomfort.py -m %s" % mode
    logging.info(str("Running command: %s" % cmd))
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    result = out.split('\n')
    for lin in result:
        if not lin.startswith('#'):
            logging.info(lin)


def set_fan(client, msg):
    logging.info("\nExecuting: set_fan()")
    client.publish("hvac/central/fan/state", str(msg.payload.decode("utf-8")))
    cmd = ""
    if str(msg.payload.decode("utf-8")).startswith('auto'):
        cmd = "python3 /usr/share/hassio/homeassistant/scripts/totalcomfort.py -f 0"
    else:
        cmd = "python3 /usr/share/hassio/homeassistant/scripts/totalcomfort.py -f 1"
    logging.info(str("Running command: %s" % cmd))
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    result = out.split('\n')
    for lin in result:
        if not lin.startswith('#'):
            logging.info(lin)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
