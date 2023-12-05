# Exercise 1: Virtual Weather-Station

Create a virtual IoT device that simulates the ambient temperature and
publishes it via MQTT. The simulation function is already predefined.
This exercise to give a simple introduction to the communication via MQTT.

<p align="center">
  <img src="https://raw.githubusercontent.com/RWTH-EBC/FiLiP/master/tutorials/ngsi_v2/e1_virtual_weatherstation/tutorials_ngsi_v2-Exercise1.drawio.png" alt="Virtual Weather Station"/>
</p>

The input sections are marked with 'ToDo'

#### Steps to complete:
1. Set up the missing parameters in the parameter section
2. Create an MQTT client using the paho-mqtt package with mqtt.Client()
3. Define a callback function that will be executed when the client
   receives message on a subscribed topic. It should decode your message
   and store the information for later in our history
   `history_weather_station`
4. Subscribe to the topic that the device will publish to
5. Create a function that publishes the simulated temperature `t_amb` and
   the corresponding simulation time `t_sim `via MQTT as a JSON
6. Run the simulation and plot