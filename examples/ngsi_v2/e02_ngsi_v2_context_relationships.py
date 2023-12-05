"""
# Examples for relationships in FIWARE ContextBroker
"""
# ## Import packages
import logging

from filip.clients.ngsi_v2 import ContextBrokerClient
from filip.models.ngsi_v2.context import ContextEntity
from filip.models.base import FiwareHeader

# ## Parameters
#
# To run this example you need a working Fiware v2 setup with a context-broker
# You can here set the address:
#
# Host address of Context Broker
CB_URL = "http://localhost:1026"

# You can here also change the used Fiware service
# FIWARE-Service
SERVICE = 'filip'
# FIWARE-Servicepath
SERVICE_PATH = '/example'

# Setting up logging
logging.basicConfig(
    level='INFO',
    format='%(asctime)s %(name)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":

    # # 1 Setup client and models
    #
    fiware_header = FiwareHeader(service=SERVICE,
                                 service_path=SERVICE_PATH)

    # ## 1.1 Store entities
    #
    with ContextBrokerClient(fiware_header=fiware_header,
                             url=CB_URL) as cb_client:
        # make sure that the server is clean
        cb_client.delete_entities(cb_client.get_entity_list())
        store_dict = [{"type": "Store",
                       "id": "urn:ngsi-ld:Store:001",
                       "address": {
                           "type": "Text",
                           "value": "Bornholmer Straße 65"
                       },
                       "location": {
                           "type": "Text",
                           "value": "[13.3986, 52.5547]"
                       },
                       "name": {
                           "type": "Text",
                           "value": "Bösebrücke Einkauf"
                       }},
                      {
                          "type": "Store",
                          "id": "urn:ngsi-ld:Store:002",
                          "address": {
                              "type": "Text",
                              "value": "Friedrichstraße 44"
                          },
                          "location": {
                              "type": "Text",
                              "value": "[13.3903, 52.5075]"
                          },
                          "name": {
                              "type": "Text",
                              "value": "Checkpoint Markt"
                          }
                      }]
        store_entities = [ContextEntity(**store) for store in store_dict]
        for entity in store_entities:
            cb_client.post_entity(entity)

    # ## 1.2 Product entities
    #
    with ContextBrokerClient(fiware_header=fiware_header) as cb_client:
        product_dict = [
            {
                "id": "urn:ngsi-ld:Product:001", "type": "Product",
                "name": {
                    "type": "Text", "value": "Beer"
                },
                "size": {
                    "type": "Text", "value": "S"
                },
                "price": {
                    "type": "Integer", "value": 99
                }
            },
            {
                "id": "urn:ngsi-ld:Product:002", "type": "Product",
                "name": {
                    "type": "Text", "value": "Red Wine"
                },
                "size": {
                    "type": "Text", "value": "M"
                },
                "price": {
                    "type": "Integer", "value": 1099
                }
            },
            {
                "id": "urn:ngsi-ld:Product:003", "type": "Product",
                "name": {
                    "type": "Text", "value": "White Wine"
                },
                "size": {
                    "type": "Text", "value": "M"
                },
                "price": {
                    "type": "Integer", "value": 1499
                }
            },
            {
                "id": "urn:ngsi-ld:Product:004", "type": "Product",
                "name": {
                    "type": "Text", "value": "Vodka"
                },
                "size": {
                    "type": "Text", "value": "XL"
                },
                "price": {
                    "type": "Integer", "value": 5000
                }
            }
        ]
        product_entities = []
        for product_entity in product_dict:
            cb_client.post_entity(ContextEntity(**product_entity))
            product_entities.append(ContextEntity(**product_entity))

    # ## 1.3 Inventory Entities
    #
    with ContextBrokerClient(fiware_header=fiware_header) as cb_client:
        inventory_dict = {
            "id": "urn:ngsi-ld:InventoryItem:001", "type": "InventoryItem",
            "refStore": {
                "type": "Relationship",
                "value": "urn:ngsi-ld:Store:001"
            },
            "refProduct": {
                "type": "Relationship",
                "value": "urn:ngsi-ld:Product:001"
            },
            "stockCount": {
                "type": "Integer", "value": 10000
            }}
        inventory_entity = ContextEntity(**inventory_dict)
        cb_client.post_entity(inventory_entity)

    # # 2 Read data from FIWARE
    #
    # ## 2.1 Inventory relationship with Store and Product
    logger.info(inventory_entity.get_relationships())

    # ## 2.2 Get entities
    #
    with ContextBrokerClient(fiware_header=fiware_header) as cb_client:
        # It should return the inventory item according to the relationship
        logger.info(
            cb_client.get_entity_list(q="refProduct==urn:ngsi-ld:Product:001"))
        logger.info(
            cb_client.get_entity_list(q="refStore==urn:ngsi-ld:Store:001"))

        # It should not return the inventory item according to the relationship
        logger.info(
            cb_client.get_entity_list(q="refStore==urn:ngsi-ld:Store:002"))

    # # 3 Delete test entities
    #
    with ContextBrokerClient(fiware_header=fiware_header) as cb_client:
        cb_client.delete_entities(store_entities)
        cb_client.delete_entities(product_entities)
        cb_client.delete_entity(entity_id=inventory_entity.id,
                                entity_type=inventory_entity.type)
