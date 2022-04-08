# Exercise 5: Virtual Thermal Zone with Control

Create a virtual IoT device that simulates a heater for your
thermal zone. The heater can be turned on and off via a simple hysteresis
controller. The devices from e4_iot_thermal_zone_sensors.py will loaded
from the stored *.json-files.

<p align="center">
  <img src="https://raw.githubusercontent.com/RWTH-EBC/FiLiP/139-Add-images-to-tutorials/tutorials/ngsi_v2/e5_iot_thermal_zone_control/tutorials_ngsi_v2-Exercise5.drawio.png" 
alt="Virtual thermal zone with control"/>
</p>


The input sections are marked with 'ToDo'

#### Steps to complete:
1. Set up the missing parameters in the parameter section
2. Retrieve the service group and device configurations of already existing
   devices from the IoT-Agent
3. Create a third device configuration for a heater holding a command
   for turning it `on` and `off`device and post it to the server
4. Create an MQTT client using the filip.client.mqtt package and register
   your service group and your devices
4. Define a callback function that will be executed when the client
   receives a command. Decode the message and set the update the state in
   simulation model. Afterwards, acknowledge the command using the api of the
   IoTAMQTTClient.
5. Add the callback for your heater device to the IoTAMQTTClient
6. Create an MQTT subscription for asynchronous communication that
   gets triggered when the temperature attribute changes.
7. Write a second callback that represents your controller. It should get
   triggered when the MQTTClient receive a notification message due to your
   subscription. Add the callback to your MQTTClient using the original
   paho-api (`message_callback_add`)
8. Run the simulation and plot