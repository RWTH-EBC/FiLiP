# # Exercise 3: Context Entities

# Create building context entity of type 'Building' according to FIWARE's
# SmartData Models with the properties: `id`, `type`, `address`, `category`,
# https://github.com/smart-data-models/dataModel.Building/blob/master/Building/doc/spec.md

# For the single properties check on the "Data Model description of
# properties" section. The input sections are marked with 'ToDo'

# #### Steps to complete:
# 1. Set up the missing parameters in the parameter section
# 2. Create an MQTT client using the paho-mqtt package with mqtt.Client()
# 3. Define a callback function that will be executed when the client
#    receives message on a subscribed topic. It should decode your message
#    and store the information for later in our history
# 4. Subscribe to the topic that the device will publish to
# 5. Create a function that publishes the simulated temperature via MQTT as a JSON
# 6. Run the simulation and plot

# ## Import packages
import json
from pathlib import Path
from filip.clients.ngsi_v2 import ContextBrokerClient
from filip.models import FiwareHeader
from filip.models.ngsi_v2.context import ContextEntity, NamedContextAttribute
from filip.utils.cleanup import clear_context_broker
from filip.utils.simple_ql import QueryString

# ## Parameters
# ToDo: Enter your context broker host and port, e.g http://localhost:1026
CB_URL = "http://localhost:1026"

# FIWARE-Service
SERVICE = 'filip_tutorial'
# FIWARE-Servicepath
# ToDo: Change the name of your service-path to something unique. If you run
#  on a shared instance this very important in order to avoid user
#  collisions. You will use this service path through the whole tutorial.
#  If you forget to change it an error will be raised!
SERVICE_PATH = '/<your_path>'

# Path to json-files to store entity data for follow up exercises
write_entities_filepath = Path("./e3_context_entities_solution_entities.json")


if __name__ == '__main__':
    # create a fiware header object
    fiware_header = FiwareHeader(service=SERVICE,
                                 service_path=SERVICE_PATH)
    # clear the state of your service and scope
    clear_context_broker(url=CB_URL, fiware_header=fiware_header)

    # ToDo: Create a context broker client and add the fiware_header
    cb_client = ContextBrokerClient(url=CB_URL, fiware_header=fiware_header)

    # Create a context entity for a `building` following the smart data models
    # specifications
    building = ContextEntity(id="urn:ngsi-ld:building:001",
                             type="Building")

    # create the property `category` to your building
    category = NamedContextAttribute(name="category",
                                     type="Array",
                                     value=["office"])

    # ToDo: create a property `address` for your building. Follow the full yaml
    #  description in the specifications. It reuses the specification from
    #  here: https://schema.org/PostalAddress
    address = NamedContextAttribute(name="address",
                                    type="PostalAddress",
                                    value={
                                        "addressCountry": "DE",
                                        "addressLocality": "Any City",
                                        "postalCode": "12345",
                                        "streetAddress": "Any Street 5"
                                    })

    # ToDo: create a `description` property for your building
    building_description = NamedContextAttribute(name="description",
                                                 type="Text",
                                                 value="Small office building "
                                                       "with good insulation "
                                                       "standard")

    # add all properties to your building using the
    # `add_attribute` function of your building object
    building.add_attributes(attrs=[building_description,
                                   category,
                                   address])

    # ToDo: Send your building model to the context broker. Check the client
    #  for the proper function
    cb_client.post_entity(entity=building)

    # Update your local building model with the one from the server
    building = cb_client.get_entity(entity_id=building.id,
                                    entity_type=building.type)

    # print your `building model` as json
    print(building.json(indent=2))

    # ToDo: create a `opening hours` property and add it to the building object
    #  in the context broker. Do not update the whole entity! In real
    #  scenarios it might have been modified by other users.
    opening_hours = NamedContextAttribute(name="openingHours",
                                          type= "array",
                                          value=[
                                              "Mo-Fr 10:00-19:00",
                                              "Sa closed",
                                              "Su closed"
                                          ])

    cb_client.update_or_append_entity_attributes(
        entity_id=building.id,
        entity_type=building.type,
        attrs=[opening_hours])

    # ToDo: retrieve and print the opening hours
    print(cb_client.get_attribute_value(entity_id=building.id,
                                        entity_type=building.type,
                                        attr_name=opening_hours.name))

    # ToDo: modify the `opening hours` of the building
    cb_client.update_attribute_value(entity_id=building.id,
                                     entity_type=building.type,
                                     attr_name=opening_hours.name,
                                     value=["Mo-Sa 10:00-19:00",
                                            "Su closed"])

    # ToDo: At this point you might have already noticed that your local
    #  building model and the building model in the context broker are out of
    #  sync. Hence, synchronize them again!
    building = cb_client.get_entity(entity_id=building.id,
                                    entity_type=building.type)

    print(building.json(indent=4))

    # ToDo: Create an entity of thermal zone and add a description property
    #  to it
    thermal_zone = ContextEntity(id="ThermalZone:001",
                                 type="ThermalZone")

    thermal_zone_description = NamedContextAttribute(name="description",
                                                     type="Text",
                                                     value="This zones covers "
                                                           "the entire building")
    thermal_zone.add_attributes(attrs=[thermal_zone_description])

    # ToDo: Create and a property that references your building model. Use the
    #  `Relationship` for type
    ref_building = NamedContextAttribute(name="refBuilding",
                                         type="Relationship",
                                         value=building.id)

    thermal_zone.add_attributes(attrs=[ref_building])

    # print all relationships of your thermal zone
    for relationship in thermal_zone.get_relationships():
        print(relationship.json(indent=2))

    # ToDo: Post your thermal zone model to the context broker
    cb_client.post_entity(entity=thermal_zone)
    thermal_zone = cb_client.get_entity(entity_id=thermal_zone.id,
                                        entity_type=thermal_zone.type)

    # ToDo: create a filter request that retrieves all entities from the
    #   server`that have `refBuilding` attribute that references your building
    #   by using the FIWARE's simple query language.
    #   `filip.utils.simple_ql` module helps you to validate your query string
    #   1. prepare the query string using the `filip.utils.simple_ql`
    #   2. use the string in a context broker request and retrieve the entities.
    query = QueryString(qs=("refBuilding", "==", building.id))
    for entity in cb_client.get_entity_list(q=query):
        print(entity.json(indent=2))

    # write entities to file and clear server state
    assert write_entities_filepath.suffix == '.json', \
        f"Wrong file extension! {write_entities_filepath.suffix}"
    write_entities_filepath.touch(exist_ok=True)
    with write_entities_filepath.open('w', encoding='utf-8') as f:
        entities = [item.dict() for item in cb_client.get_entity_list()]
        json.dump(entities, f, ensure_ascii=False, indent=2)

    clear_context_broker(url=CB_URL, fiware_header=fiware_header)
