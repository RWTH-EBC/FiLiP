import logging
from typing import List
from requests import RequestException
from filip.cb import ContextBrokerClient
from filip.core.models import FiwareHeader, ContextEntity, ContextAttribute
from filip.core.simple_query_language import QueryString

logger = logging.getLogger(__name__)


def setup():
    """
    Get version of context broker
    """
    logger.info("------Setting up clients------")
    with ContextBrokerClient(
            fiware_header=FiwareHeader(service='filip',
                                       service_path='/testing')) as cb_client:
        for key, value in cb_client.get_version().items():
            print("Context broker version" + value["version"] + "at url " +
                  cb_client.base_url)


def create_entities():
    """
    Create entities
    """

    with ContextBrokerClient(
            fiware_header=FiwareHeader(service='filip',
                                       service_path='/testing')) as cb_client:
        room1 = {"id": "Room1",
                 "type": "Room",
                 "temperature": {"value": 11,
                                 "type": "Float"},
                 "pressure": {"value": 111,
                              "type": "Integer"}
                 }

        room2 = {"id": "Room2",
                 "type": "Room",
                 "temperature": {"value": 22,
                                 "type": "Float"},
                 "pressure": {"value": 222,
                              "type": "Integer"}
                 }

        room3 = {"id": "Room3",
                 "type": "Room",
                 "temperature": {"value": 33,
                                 "type": "Float"},
                 "pressure": {"value": 333,
                              "type": "Integer"}
                 }
        logger.info("------Creating example entities------")

        room1_entity = ContextEntity(**room1)
        room2_entity = ContextEntity(**room2)
        room3_entity = ContextEntity(**room3)

        logger.info("------Posting example entities------")

        cb_client.post_entity(entity=room1_entity)
        cb_client.post_entity(entity=room2_entity)
        cb_client.post_entity(entity=room3_entity)

        return [room1_entity, room2_entity, room3_entity]


def filter_entities():
    """
    Retrieve and filter entities
    Returns:

    """
    with ContextBrokerClient(
            fiware_header=FiwareHeader(service='filip',
                                       service_path='/testing')) as cb_client:
        logger.info("------Get all entities from context broker------")
        logger.info(cb_client.get_entity_list())

        logger.info("------Get entities by id------")
        logger.info(cb_client.get_entity_list(entity_ids=["Room1"]))

        logger.info("------Get entities by type------")
        logger.info(cb_client.get_entity_list(entity_types=["Room"]))

        logger.info("------Get entities by id pattern------")
        logger.info(cb_client.get_entity_list(id_pattern="^Room[2-5]"))

        logger.info("------Get entities by query expression------")
        query = QueryString(qs=[('temperature', '>', 22)])
        logger.info(cb_client.get_entity_list(q=query))

        logger.info("------Get attributes of entities------")
        logger.info(cb_client.get_entity_attributes(entity_id="Room1"))


def update_entity(entity: ContextEntity):
    """
    Update entitites
    Args:
        entity:
    Returns:

    """
    with ContextBrokerClient(
            fiware_header=FiwareHeader(service='filip',
                                       service_path='/testing')) as cb_client:
        entity.add_properties({'Space': ContextAttribute(
            type='Number', value=111)})

        logger.info("------Updating value of an attribute of an entity------")

        logger.info(cb_client.update_attribute_value(entity_id=entity.id,
                                                     attr_name="temperature",
                                                     value=12))

        logger.info("------Adding a new attribute to an entity------")
        logger.info(cb_client.update_entity(entity=entity))

        logger.info("------Checking if new attribute is added------")
        logger.info(cb_client.get_entity_attributes(entity_id=entity.id))


def error_check(entity: ContextEntity):
    """
    Check error messages
    Args:
        entity:
    Returns:

    """

    with ContextBrokerClient(
            fiware_header=FiwareHeader(service='filip',
                                       service_path='/testing')) as cb_client:
        try:
            logger.info("-----Should return an error "
                        "for non existing id------")
            logger.info(cb_client.get_entity(entity_id="Room5"))
        except RequestException:
            try:
                logger.info("-----Should return an error "
                            "for non existing type-----")
                logger.info(cb_client.get_entity(entity_id=entity.id,
                                                 entity_type="Surface"))
            except RequestException:
                try:
                    logger.info("------Should return an error for non "
                                "existing attribute name------")
                    logger.info(
                        cb_client.get_attribute_value(entity_id=entity.id,
                                                      attr_name="area"))
                except RequestException:
                    pass


def delete_entities(entities_to_delete: List[ContextEntity]):
    """
    Clean up
    Args:
        entities_to_delete:

    Returns:

    """
    with ContextBrokerClient(
            fiware_header=FiwareHeader(service='filip',
                                       service_path='/testing')) as cb_client:
        logger.info("Deleting all test entities")
        for entity in entities_to_delete:
            cb_client.delete_entity(entity_id=entity.id)
        return


if __name__ == "__main__":
    logger.info("------EXAMPLE ORION------")

    setup()

    entities = create_entities()

    filter_entities()

    update_entity(entities[0])

    error_check(entities[0])

    delete_entities(entities)
