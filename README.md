# hassio-mqtt-honeywell-

Home assistant thermostat:
<li>Use python script to connect to total comfort website (totalcomfort.py)
<li>Use python script to generate mqtt wrapper that calls totalcomfort.py (climate2mqtt.py)
<li>Create systemd service that launches climate2mqtt.py (climate2mqtt.service)
<li>Use mosquitto broker addon in hassio
<li>Create MQTT HVAC device in HA (climate_configuration.yaml)
<li>Create generic HA inputs for user control to be picked up by node red (climate_configuration.yaml)
<li>Use node-red in HA to make HA publish MQTT topics through MQTT HVAC that get picked up by climate2mqtt.py, which in turn executes commands that call the total comfort website

