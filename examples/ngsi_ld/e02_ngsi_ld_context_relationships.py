"""
# Examples for relationships in FIWARE ContextBroker
"""
# ## Import packages
import logging

from filip.clients.ngsi_ld.cb import ContextBrokerLDClient
from filip.models.base import FiwareLDHeader
from filip.utils.cleanup import clear_context_broker_ld
from filip.models.ngsi_ld.context import (
    ContextLDEntity
)
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
    fiware_header = FiwareLDHeader(ngsild_tenant=SERVICE)

    # ## 1.1 Store entities
    #
    with ContextBrokerLDClient(fiware_header=fiware_header, url=CB_URL) as cb_client:
        # make sure that the server is clean
        clear_context_broker_ld(cb_ld_client=cb_client)
        store_dict = [
            {
                "type": "Store",
                "id": "urn:ngsi-ld:Store:001",
                "address": {"type": "Property", "value": "Bornholmer Straße 65"},
                "location": {"type": "Property", "value": "[13.3986, 52.5547]"},
                "name": {"type": "Property", "value": "Bösebrücke Einkauf"},
            },
            {
                "type": "Store",
                "id": "urn:ngsi-ld:Store:002",
                "address": {"type": "Property", "value": "Friedrichstraße 44"},
                "location": {"type": "Property", "value": "[13.3903, 52.5075]"},
                "name": {"type": "Property", "value": "Checkpoint Markt"},
            },
        ]
        store_entities = [ContextLDEntity(**store) for store in store_dict]
        for entity in store_entities:
            cb_client.post_entity(entity)

    # ## 1.2 Product entities
    #
    with ContextBrokerLDClient(fiware_header=fiware_header, url=CB_URL) as cb_client:
        product_dict = [
            {
                "id": "urn:ngsi-ld:Product:001",
                "type": "Product",
                "name": {"type": "Property", "value": "Beer"},
                "size": {"type": "Property", "value": "S"},
                "price": {"type": "Property", "value": 99},
            },
            {
                "id": "urn:ngsi-ld:Product:002",
                "type": "Product",
                "name": {"type": "Property", "value": "Red Wine"},
                "size": {"type": "Property", "value": "M"},
                "price": {"type": "Property", "value": 1099},
            },
            {
                "id": "urn:ngsi-ld:Product:003",
                "type": "Product",
                "name": {"type": "Property", "value": "White Wine"},
                "size": {"type": "Property", "value": "M"},
                "price": {"type": "Property", "value": 1499},
            },
            {
                "id": "urn:ngsi-ld:Product:004",
                "type": "Product",
                "name": {"type": "Property", "value": "Vodka"},
                "size": {"type": "Property", "value": "XL"},
                "price": {"type": "Property", "value": 5000},
            },
        ]
        product_entities = []
        for product_entity in product_dict:
            cb_client.post_entity(ContextLDEntity(**product_entity))
            product_entities.append(ContextLDEntity(**product_entity))

    # ## 1.3 Inventory Entities
    #
    with ContextBrokerLDClient(fiware_header=fiware_header, url=CB_URL) as cb_client:
        inventory_dict = {
            "id": "urn:ngsi-ld:InventoryItem:001",
            "type": "InventoryItem",
            "refStore": {"type": "Relationship", "object": "urn:ngsi-ld:Store:001"},
            "refProduct": {"type": "Relationship", "object": "urn:ngsi-ld:Product:001"},
            "stockCount": {"type": "Property", "value": 10000},
        }
        inventory_entity = ContextLDEntity(**inventory_dict)
        cb_client.post_entity(inventory_entity)

    # # 2 Read data from FIWARE
    #
    # ## 2.1 Inventory relationship with Store and Product
    logger.info(inventory_entity.get_relationships())

    # ## 2.2 Get entities
    #
    with ContextBrokerLDClient(fiware_header=fiware_header, url=CB_URL) as cb_client:
        # It should return the inventory item according to the relationship
        query = 'refProduct=="urn:ngsi-ld:Product:001"'
        logger.info(cb_client.get_entity_list(q=query))

        query = 'refStore=="urn:ngsi-ld:Store:001"'
        logger.info(cb_client.get_entity_list(q=query))

        # It should not return the inventory item according to the relationship
        query='refStore=="urn:ngsi-ld:Store:002"'
        logger.info(cb_client.get_entity_list(q=query))

    # # 3 Delete test entities
    #
    with ContextBrokerLDClient(fiware_header=fiware_header, url=CB_URL) as cb_client:
        clear_context_broker_ld(cb_ld_client=cb_client)
