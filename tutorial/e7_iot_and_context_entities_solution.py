
# Path to json-files to store entity data for follow up exercises
read_entities_filepath = Path("./e3_context_entities_solution_entities.json")
write_entities_filepath = Path("./e4_iot_thermal_zone_sensors_entities.json")
write_groups_filepath = Path("./e4_iot_thermal_zone_sensors_groups.json")
write_devices_filepath = Path("./e4_iot_thermal_zone_sensors_devices.json")


# restore data from json-file
entities = parse_file_as(List[ContextEntity],
                         path=read_entities_filepath)
# create a context broker client and add the fiware_header
cbc = ContextBrokerClient(url=CB_URL, fiware_header=fiware_header)
cbc.update(entities=entities, action_type='append')

# check if successfully restored
assert len(cbc.get_entity_list()) > 0, "failed to restore entity data"


# ToDo: Define a callback function that will be executed when the client
#  receives message on a subscribed topic. It should decode your message
#  and store the information for later in our history
#  Note: do not change function's signature!
def on_message_weather_station(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    json_payload = json.loads(payload)
    # history_weather_station.append(json_payload)


def on_message_zone_temperature_sensor(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    json_payload = json.loads(payload)
    # history_zone_temperature_sensor.append(json_payload)


    # add your callback function to the client
    mqttc.message_callback_add(sub=topic_weather_station,
                               callback=on_message_weather_station)
    mqttc.message_callback_add(sub=topic_zone_temperature_sensor,
                               callback=on_message_zone_temperature_sensor)