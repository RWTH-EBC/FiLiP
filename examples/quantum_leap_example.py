import logging

from filip.models.ngsi_v2.context import ContextEntity, NotificationMessage
from filip.models.base import FiwareHeader
from filip.clients.ngsi_v2 import ContextBrokerClient, QuantumLeapClient

# Setting up logging
logging.basicConfig(
    level='INFO',
    format='%(asctime)s %(name)s %(levelname)s: %(message)s')

logger = logging.getLogger(__name__)


def setup(fiware_header: FiwareHeader):
    logger.info("------Setting up clients------")


    with QuantumLeapClient(fiware_header=fiware_header) as ql_client:
        print("Quantum Leap " + ql_client.get_version().__str__() + " at url " +
              ql_client.base_url)

    with ContextBrokerClient(fiware_header=fiware_header) as cb_client:
        for key, value in cb_client.get_version().items():
            print("Context broker version" + value["version"] + "at url " +
                  cb_client.base_url)


def create_entity(fiware_header: FiwareHeader):

    with ContextBrokerClient(fiware_header=fiware_header) as cb_client:
        hall = {"id": "Hall_1",
                "type": "Room",
                "temperature": {"value": 11,
                                "type": "Integer"},
                }

        logger.info("------Creating example entity------")
        hall_entity = ContextEntity(**hall)
        logger.info("------Posting example entity------")
        cb_client.post_entity(hall_entity)
        return cb_client.get_entity(hall_entity.id)


def post_subscription(fiware_header: FiwareHeader, entity_id: str):
    with QuantumLeapClient(fiware_header=fiware_header) as ql_client:
        logger.info("------Posting subscription to context broker via QL------")

        ql_client.post_subscription(entity_id=entity_id)

def get_subscriptions(fiware_header: FiwareHeader):
    with ContextBrokerClient(fiware_header=fiware_header) as cb_client:
        logger.info("------Getting all subscriptions from context broker------")
        return cb_client.get_subscription_list()

def notify_ql(fiware_header: FiwareHeader, subscription_list, entity_in_cb):
    with QuantumLeapClient(fiware_header=fiware_header) as \
            ql_client:
        logger.info("------Notify QL-----")
        for sub in subscription_list:
            for entity in sub.subject.entities:
                if entity.id == entity_in_cb.id:
                    try:
                        ql_client.post_notification(
                            notification=NotificationMessage(
                                data=[entity_in_cb],
                                subscriptionId=sub.id))
                        return sub.id
                    except:
                        logger.error("Can not notify QL")


def get_historical_data(fiware_header: FiwareHeader, entity_in_cb):
    with QuantumLeapClient(fiware_header=fiware_header) as ql_client:

        logger.info("------Historical data from QL------")
        try:
            print(ql_client.get_entity_by_id(entity_in_cb.id))
            print(ql_client.get_entity_values_by_id(entity_in_cb.id))
            print(ql_client.get_entity_attr_by_id(entity_in_cb.id,
                                                  "temperature"))
            print(ql_client.get_entity_attr_values_by_id(
                entity_in_cb.id, attr_name="temperature"))
            print(ql_client.get_entity_attr_by_type(entity_in_cb.type,
                                                    attr_name="temperature"))
            print(ql_client.get_entity_attr_values_by_type(entity_in_cb.type,
                                                           "temperature"))
        except:
            logger.info("There might be no historical data for some calls.")


def delete_entities_ql(fiware_header: FiwareHeader, entity_in_ql):
    with QuantumLeapClient(fiware_header=fiware_header) as ql_client:
        logger.info("------Deleting example entity data from crate------")
        try:
            ql_client.delete_entity(entity_id=entity_in_ql.id,
                                    entity_type=entity_in_ql.type)
        except:
            logger.error("Can not delete data from QL")


def cleanup_cb(fiware_header: FiwareHeader, entity_id, subscription_id):
    with ContextBrokerClient(fiware_header=fiware_header) as cb_client:
        logger.info("------Deleting example entity from context broker------")
        try:
            cb_client.delete_entity(entity_id=entity_id)
        except:
            logger.error("Can not delete entity from context broker")

        logger.info("------Deleting subscription from context broker------")
        try:
            cb_client.delete_subscription(subscription_id)
        except:
            logger.error("Can not delete subscription from context broker.")


if __name__ == "__main__":
    print("------EXAMPLE QUANTUM LEAP------")

    fiware_header = FiwareHeader(service='filip', service_path='/testing')

    setup(fiware_header=fiware_header)

    created_entity = create_entity(fiware_header=fiware_header)

    post_subscription(fiware_header=fiware_header,
                      entity_id=created_entity.id)

    list_of_subscriptions = get_subscriptions(fiware_header=fiware_header)

    sub_id = notify_ql(fiware_header=fiware_header,
                       subscription_list=list_of_subscriptions,
                       entity_in_cb=created_entity)

    get_historical_data(created_entity)

    delete_entities_ql(created_entity)

    cleanup_cb(created_entity.id, sub_id)
