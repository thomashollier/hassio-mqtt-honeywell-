# hassio-mqtt-honeywell-

Home assistant thermostat:
-Use python script to connect to total comfort website (totalcomfort.py)
-Use python script to generate mqtt wrapper that calls totalcomfort.py (climate2mqtt.py)
-Create systemd service that launches climate2mqtt.py
-Use mosquitto broker addon in hassio
-Create MQTT HVAC device in HA
-Create generic HA inputs for user control to be picked up by node red
-Use node-red in HA to make HA publish MQTT topics through MQTT HVAC that get picked up by climate2mqtt.py, which in turn executes commands that call the total comfort website

