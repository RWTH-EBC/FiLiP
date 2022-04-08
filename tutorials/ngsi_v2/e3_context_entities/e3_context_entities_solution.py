"""
# # Exercise 3: Context Entities and Relationships

# Create building context entity of type 'Building' according to FIWARE's
# SmartData Models with the properties: `id`, `type`, `address`, `category`,
# https://github.com/smart-data-models/dataModel.Building/blob/master/Building/doc/spec.md

# For the single properties check on the "Data Model description of
# properties" section. The input sections are marked with 'ToDo'

# #### Steps to complete:
# 1. Set up the missing parameters in the parameter section
# 2. Find the Building data model online:
#    https://github.com/smart-data-models/dataModel.Building/blob/master/Building/doc/spec.md
# 3. Create a `ContextEntity` object for your building
# 4. Create the required `ContextAttributes` and add them to your building model
# 5. Create a `ContextBrokerClient` and add post your building to the
#    ContextBroker. Afterwards, check if the Context Broker returns the
#    correct information about your building
# 6. Create an `opening hours` attribute add them to the server
# 7. Retrieve the `opening hours` manipulate them and update the model at the
#    server
# 8. Repeat the procedure with a thermal zone. Currently, the smart data
#    models hold no definition of a thermal zone. Therefore, we first only add a
#    description attribute.
# 9. Add a `Relationship` attribute to your thermal zone with name
#    `refBuilding` and type `Relationship` pointing to your building and post
#    the model to the context broker
# 10. Add a `Relationship` attribute to your building with name
#    `hasZone` and type `Relationship` pointing to your thermal zone and
#    update the model in the context broker.
# 11. Update the thermal zone and the building in the context broker
# 12. Retrieve the data by using query statements for their relationships.
"""

# ## Import packages
import json
from pathlib import Path
# filip imports
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
SERVICE_PATH = '/your_path'

# ToDo: Path to json-files to store entity data for follow up exercises,
#  e.g. ./e3_my_entities.json
WRITE_ENTITIES_FILEPATH = Path("../e3_context_entities_solution_entities.json")

# ## Main script
if __name__ == '__main__':
    # create a fiware header object
    fiware_header = FiwareHeader(service=SERVICE,
                                 service_path=SERVICE_PATH)
    # clear the state of your service and scope
    clear_context_broker(url=CB_URL, fiware_header=fiware_header)

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

    # ToDo: Create a context broker client and add the fiware_header
    cbc = ContextBrokerClient(url=CB_URL, fiware_header=fiware_header)
    # ToDo: Send your building model to the context broker. Check the client
    #  for the proper function
    cbc.post_entity(entity=building)

    # Update your local building model with the one from the server
    building = cbc.get_entity(entity_id=building.id,
                              entity_type=building.type)

    # print your `building model` as json
    print(f"This is your building model: \n {building.json(indent=2)} \n")

    # ToDo: create a `opening hours` property and add it to the building object
    #  in the context broker. Do not update the whole entity! In real
    #  scenarios it might have been modified by other users.
    opening_hours = NamedContextAttribute(name="openingHours",
                                          type="array",
                                          value=[
                                              "Mo-Fr 10:00-19:00",
                                              "Sa closed",
                                              "Su closed"
                                          ])

    cbc.update_or_append_entity_attributes(
        entity_id=building.id,
        entity_type=building.type,
        attrs=[opening_hours])

    # ToDo: retrieve and print the opening hours
    hours = cbc.get_attribute_value(entity_id=building.id,
                                    entity_type=building.type,
                                    attr_name=opening_hours.name)
    print(f"Your opening hours: {hours} \n" )

    # ToDo: modify the `opening hours` of the building
    cbc.update_attribute_value(entity_id=building.id,
                               entity_type=building.type,
                               attr_name=opening_hours.name,
                               value=["Mo-Sa 10:00-19:00",
                                      "Su closed"])

    # ToDo: At this point you might have already noticed that your local
    #  building model and the building model in the context broker are out of
    #  sync. Hence, synchronize them again!
    building = cbc.get_entity(entity_id=building.id,
                              entity_type=building.type)

    # print your building
    print(f"Your updated building model: \n {building.json(indent=2)}")

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
    #  `Relationship` for type and `refBuilding` for its name
    ref_building = NamedContextAttribute(name="refBuilding",
                                         type="Relationship",
                                         value=building.id)
    thermal_zone.add_attributes(attrs=[ref_building])

    # print all relationships of your thermal zone
    for relationship in thermal_zone.get_relationships():
        print(f"Relationship properties of your thermal zone mdoel: \n "
              f"{relationship.json(indent=2)} \n")

    # ToDo: Post your thermal zone model to the context broker
    cbc.post_entity(entity=thermal_zone)
    thermal_zone = cbc.get_entity(entity_id=thermal_zone.id,
                                  entity_type=thermal_zone.type)

    # ToDo: Create and a property that references your thermal zone. Use the
    #  `Relationship` for type and `hasZone` for its name. Make sure that
    #  your local model and the server model are in sync afterwards.
    ref_zone = NamedContextAttribute(name="hasZone",
                                     type="Relationship",
                                     value=thermal_zone.id)
    cbc.update_or_append_entity_attributes(entity_id=building.id,
                                           entity_type=building.type,
                                           attrs=[ref_zone])
    building = cbc.get_entity(entity_id=building.id,
                              entity_type=building.type)

    # ToDo: create a filter request that retrieves all entities from the
    #   server`that have `refBuilding` attribute that references your building
    #   by using the FIWARE's simple query language.
    #   `filip.utils.simple_ql` module helps you to validate your query string
    #   1. prepare the query string using the `filip.utils.simple_ql`
    #   2. use the string in a context broker request and retrieve the entities.
    query = QueryString(qs=("refBuilding", "==", building.id))
    for entity in cbc.get_entity_list(q=query):
        print(f"All entities referencing the building: "
              f"\n {entity.json(indent=2)}\n")

    # ToDo: create a filter request that retrieves all entities from the
    #   server`that have `hasZone' attribute that references your thermal zone
    #   by using the FIWARE's simple query language.
    #   `filip.utils.simple_ql` module helps you to validate your query string
    #   1. prepare the query string using the `filip.utils.simple_ql`
    #   2. use the string in a context broker request and retrieve the entities.
    query = QueryString(qs=("hasZone", "==", thermal_zone.id))
    for entity in cbc.get_entity_list(q=query):
        print(f"All entities referencing the thermal zone: "
              f"\n {entity.json(indent=2)} \n")

    # write entities to file and clear server state
    assert WRITE_ENTITIES_FILEPATH.suffix == '.json', \
        f"Wrong file extension! {WRITE_ENTITIES_FILEPATH.suffix}"
    WRITE_ENTITIES_FILEPATH.touch(exist_ok=True)
    with WRITE_ENTITIES_FILEPATH.open('w', encoding='utf-8') as f:
        entities = [item.dict() for item in cbc.get_entity_list()]
        json.dump(entities, f, ensure_ascii=False, indent=2)

    clear_context_broker(url=CB_URL, fiware_header=fiware_header)
