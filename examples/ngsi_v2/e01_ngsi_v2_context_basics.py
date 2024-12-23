"""
# Example how to use Entity-models and interact with the Orion ContextBroker
"""

# ## Import packages
import logging

from filip.clients.ngsi_v2 import ContextBrokerClient
from filip.models.base import FiwareHeader, DataType
from filip.models.ngsi_v2.context import (
    ContextEntity,
    ContextAttribute,
    NamedContextAttribute,
)
from filip.utils.simple_ql import QueryString
from filip.config import settings

# ## Parameters
#
# To run this example, you need a working Fiware v2 setup with a context-broker
# You can set the address here:
#
# Host address of Context Broker
CB_URL = settings.CB_URL

# You can also change the used Fiware service
# FIWARE-Service
SERVICE = "filip"
# FIWARE-Service path
SERVICE_PATH = "/example"

# Setting up logging
logging.basicConfig(
    level="INFO",
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":

    # # 1 Setup Client
    #
    # create the client, for more details view the example: e01_http_clients.py
    fiware_header = FiwareHeader(service=SERVICE, service_path=SERVICE_PATH)
    cb_client = ContextBrokerClient(url=CB_URL, fiware_header=fiware_header)
    # View version
    for key, value in cb_client.get_version().items():
        logger.info(
            f"Context broker version: {value['version']} at url: "
            f"{cb_client.base_url}"
        )

    # # 2 Create Entities
    #
    # ## 2.1 Build Models
    #
    # Entities can be created by:
    #
    # ### 2.1.1 Passing a dict:
    #
    room1_dictionary = {
        "id": "urn:ngsi-ld:Room:001",
        "type": "Room",
        "temperature": {"value": 11, "type": "Float"},
        "pressure": {"value": 111, "type": "Integer"},
    }
    room1_entity = ContextEntity(**room1_dictionary)

    # ### 2.1.2 Using the constructor and interfaces
    #
    room2_entity = ContextEntity(id="urn:ngsi-ld:Room:002", type="Room")
    temp_attr = NamedContextAttribute(name="temperature", value=22, type=DataType.FLOAT)
    pressure_attr = NamedContextAttribute(name="pressure", value=222, type="Integer")
    room2_entity.add_attributes([temp_attr, pressure_attr])

    # ## 2.2 Post Entities
    #
    logger.info(f"Entity list before posting to CB: {cb_client.get_entity_list()}")
    cb_client.post_entity(entity=room1_entity)
    cb_client.post_entity(entity=room2_entity)

    # # 3 Access entities in Fiware
    #
    # Get all entities from context broker
    logger.info(f"Entity list after posting to CB: {cb_client.get_entity_list()}")

    # Get entities by id
    logger.info(
        f'Entities with ID "urn:ngsi-ld:Room:001": '
        f'{cb_client.get_entity_list(entity_ids=["urn:ngsi-ld:Room:001"])}'
    )

    # Get entities by type
    logger.info(
        f'Entities by type "Room": {cb_client.get_entity_list(entity_types=["Room"])}'
    )

    # Get entities by id pattern
    # The regular expression filters the rooms that have the id number 2 through 5
    # with the prefix 'urn:ngsi-ld:Room:'
    logger.info(
        f'Entities with id pattern "^urn:ngsi-ld:Room:00[2-5]": '
        f'{cb_client.get_entity_list(id_pattern="^urn:ngsi-ld:Room:00[2-5]")}'
    )

    # Get entities by query expression
    query = QueryString(qs=[("temperature", ">=", 22)])
    logger.info(
        f"Entities with temperature >= 22: {cb_client.get_entity_list(q=query)}"
    )

    # Get attributes of entities
    logger.info(
        f'Attributes of entities: {cb_client.get_entity_attributes(entity_id="urn:ngsi-ld:Room:001")}'
    )

    # Trying to access non-existing ids or attributes will always throw
    # a request error

    # # 4 Changing Entities
    #
    # ## 4.1 Updating

    entity = room2_entity
    entity.add_attributes({"Space": ContextAttribute(type="Number", value=111)})
    # ### 4.1.1 Updating directly
    #
    # Using the Filip interface, we can update different properties of our
    # entity directly in the live version in FIWARE. A few examples of what
    # is possible are listed here:

    # Updating value of an attribute of an entity
    logger.info(
        cb_client.update_attribute_value(
            entity_id=room1_entity.id, attr_name="temperature", value=12
        )
    )
    # Deleting attributes
    # logger.info(cb_client.delete_entity_attribute(entity_id=room1_entity.id,
    #                                               attr_name="temperature"))
    # ### 4.1.2 Updating the model
    #
    # Most of the time it is more convenient to update our local model,
    # and let the library handle all the needed updates to synchronise the
    # live state to the model state.
    # Hereby it is tried to only make changes that were done locally,
    # keeping as much of the current live state as possible

    # When accessing an attribute a new object is created. We need to
    # manually transmit the made changes.
    temp_attr = room2_entity.get_attribute("temperature")
    temp_attr.value = 15
    room2_entity.update_attribute([temp_attr])

    room2_entity.delete_attributes(["pressure"])

    # all changes are transmitted with one methode call
    cb_client.patch_entity(room2_entity)

    # ## 4.2 Deleting
    #
    # To delete an entry in Fiware, we can call:
    cb_client.delete_entity(entity_id=room2_entity.id, entity_type=room2_entity.type)
    cb_client.delete_entity(entity_id=room1_entity.id, entity_type=room1_entity.type)
