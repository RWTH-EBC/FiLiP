import logging

from models import ContextEntity
from core.models import FiwareHeader
from timeseries import QuantumLeapClient
from cb import ContextBrokerClient
from timeseries.models import NotificationMessage

logger = logging.getLogger(__name__)


def setup():
    logger.info("------Setting up clients------")
    with QuantumLeapClient(fiware_header=FiwareHeader(service='filip',
                                                      service_path='/testing')) as \
            ql_client:
        print("Quantum Leap " + ql_client.get_version().__str__() + " at url " +
              ql_client.base_url)
    with ContextBrokerClient(fiware_header=FiwareHeader(service='filip',
                                                        service_path='/testing')) as \
            cb_client:
        for key, value in cb_client.get_version().items():
            print("Context broker version" + value["version"] + "at url " +
                  cb_client.base_url)


def create_entity():
    """
    Function creates a test entity and registers it with the context broker
    """
    with ContextBrokerClient(fiware_header=FiwareHeader(service='filip',
                                                        service_path='/testing')) as \
            cb_client:
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


def post_subscription(entity_id: str):
    """
    Function posts a test subscription

    """
    with QuantumLeapClient(fiware_header=FiwareHeader(service='filip',
                                                      service_path='/testing')) as \
            ql_client:
        logger.info("------Posting subscription to context broker via QL------")

        ql_client.post_subscription(entity_id=entity_id)
        return


def get_subscriptions():
    with ContextBrokerClient(fiware_header=FiwareHeader(service='filip',
                                                        service_path='/testing')) as \
            cb_client:
        logger.info("------Getting all subscriptions from context broker------")
        return cb_client.get_subscription_list()


def notify_ql(subscription_list, entity_in_cb):
    with QuantumLeapClient(fiware_header=FiwareHeader(service='filip',
                                                      service_path='/testing')) as \
            ql_client:
        logger.info("------Notify QL-----")
        for sub in subscription_list:
            for entity in sub.subject.entities:
                if entity.id == entity_in_cb.id:
                    try:
                        ql_client.post_notification(
                            notification=NotificationMessage(data=[entity_in_cb],
                                                             subscriptionId=sub.id))
                        return sub.id
                    except:
                        logger.error("Can not notify QL")


def get_historical_data(entity_in_cb):
    with QuantumLeapClient(fiware_header=FiwareHeader(service='filip',
                                                      service_path='/testing')) as \
            ql_client:
        logger.info("------Historical data from QL------")
        try:
            print(ql_client.get_entity_attrs_by_id(entity_in_cb.id))
            print(ql_client.get_entity_attrs_values_by_id(entity_in_cb.id))
            print(ql_client.get_entity_attr_by_id(entity_in_cb.id, "temperature"))
            print(ql_client.get_entity_attr_values_by_id(entity_in_cb.id,
                                                         attr_name="temperature"))
            print(ql_client.get_entity_attr_by_type(entity_in_cb.type,
                                                    attr_name="temperature"))
            print(ql_client.get_entity_attr_values_by_type(entity_in_cb.type,
                                                           "temperature"))
        except:
            logger.info("There might be no historical data for some calls.")


def delete_entities_ql(entity_in_ql):
    with QuantumLeapClient(fiware_header=FiwareHeader(service='filip',
                                                      service_path='/testing')) as \
            ql_client:
        logger.info("------Deleting example entity data from crate------")
        try:
            ql_client.delete_entity(entity_id=entity_in_ql.id,
                                    entity_type=entity_in_ql.type)
        except:
            logger.error("Can not delete data from QL")


def cleanup_cb(entity_id, subscription_id):
    with ContextBrokerClient(fiware_header=FiwareHeader(service='filip',
                                                        service_path='/testing')) as \
            cb_client:
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

# TODO: Delete excess code
# def update_attribute(orion_cb:object, entity:object, attribute_name:str):
#     # ToDO: Add attribute change for string attributes
#     """
#     :param orion_cb: And instance of the orion context broker
#     :param entity:
#     :param attribute_name:
#     :return:
#     """
#     for i in range(0,10):
#             value = i*3
#             print("new 'height' value: " + str(value))
#             orion_cb.update_attribute(entity.id, attribute_name, value)
#             time.sleep(1)
#
#
# def get_timeseries_data_as_df(quantum:object, entity:object, attribute:str=None):
#     """
#
#     :param quantum: An instance of quantumleap where the timeseries data should be
#     obtained from
#     :param entity:  The entity of which the data should be obtained
#     :param attribute: The attribute of which the data should be obtained, if none
#     given, the attributes of all data is obtained
#     :return: dataframe
#     """
#     if attribute:
#         ts_dict = quantum.get_timeseries(entity.id, attribute)
#     else:
#         ts_dict = quantum.get_timeseries(entity.id)
#     dataframe = utils.timeseries_to_pandas(ts_dict)
#     return dataframe
#
#
# def create_example_dataframe():
#     """
#     This is a helper function to display a example for plot_timeseries.py
#     :return: a dataframe
#     """
#     CONFIG = config.Config()
#     ORION_CB = cb.ContextBroker(CONFIG)
#     oak = create_entity(ORION_CB)
#     quantum = ts.QuantumLeapClient(CONFIG)
#     """
#     Function creates a test entity and registers it with the context broker
#     :param orion_cb: A Orion Context Broker Instance
#     :return: An NGSI Entity object
#     """
#     oak = {"id": "Oak_nr_44",
#            "type": "Tree",
#            "height": {"value" : 11,
#                       "type" : "Integer" },
#            "age": {"value": 7.5,
#                    "type": "Float"},
#            "leaves": {"value": "green",
#                       "type": "String"},
#            }
#     oak_entity = cb.Entity(oak)
#
#     ORION_CB.post_json(oak_entity.get_json())
#     return oak_entity
#
# def create_subscription(orion_cb:object, quantum:object, entity:object,
#                         notify_url:str, throttinling=0,
#                         expires:object =datetime.datetime(2020, 12, 24,
#                         18).isoformat() ,
#                         metadata:list=["dateCreated", "dateModified"] ):
#     """
#     Function creates a test subscription
#     :param orion_cb: An instance of the Context Broker, where the subscriptions is
#     registered
#     :param quantum: An instance of Quantumleap to manage timeseries data
#     :param entity: the entity for which the subscription should be registered
#     :param notify_url: ne url which should be notified, if the context broker
#     registers any change in the entity attributes
#     :param throttinling: defines the rate at which changes are sampled, e,g. every 5
#     seconds
#     :param expires:  How long the subscription is valid
#     :param metadata: add metadate to include when the attribute was changed
#     :return: a subscription_id
#     """
#
#
#     subscription =quantum.create_subscription_object(entity, notify_url,
#                                        throttinling=throttinling,
#                                        expires=expires)
#     subscription.notification.metadata = metadata
#     sub_id = orion_cb.create_subscription(subscription.get_json())
#     return sub_id
#
# def update_attribute(orion_cb:object, entity:object, attribute_name:str):
#     # ToDO: Add attribute change for string attributes
#     """
#     :param orion_cb: And instance of the orion context broker
#     :param entity:
#     :param attribute_name:
#     :return:
#     """
#     for i in range(0,10):
#             value = i*3
#             print("new 'height' value: " + str(value))
#             orion_cb.update_attribute(entity.id, attribute_name, value)
#             time.sleep(1)
#
#
# def get_timeseries_data_as_df(quantum:object, entity:object, attribute:str=None):
#     """
#
#     :param quantum: An instance of quantumleap where the timeseries data should be
#     obtained from
#     :param entity:  The entity of which the data should be obtained
#     :param attribute: The attribute of which the data should be obtained, if none
#     given, the attributes of all data is obtained
#     :return: dataframe
#     """
#     if attribute:
#         ts_dict = quantum.get_timeseries(entity.id, attribute)
#     else:
#         ts_dict = quantum.get_timeseries(entity.id)
#     dataframe = utils.timeseries_to_pandas(ts_dict)
#     return dataframe
#
#
# def create_example_dataframe():
#     """
#     This is a helper function to display a example for plot_timeseries.py
#     :return: a dataframe
#     """
#     CONFIG = config.Config()
#     ORION_CB = orion.ContextBroker(CONFIG)
#     oak = create_entity(ORION_CB)
#     quantum = ts.QuantumLeapClient(CONFIG)
#
#     notify_url =  "http://quantumleap:8668/v2/notify"
#
#     sub_id = create_subscription(orion_cb=ORION_CB, quantum=quantum, entity=oak,
#     notify_url=notify_url)
#
#     update_attribute(orion_cb=ORION_CB, entity=oak, attribute_name="height")
#
#     ORION_CB.update_attribute(oak.id, "leaves", "brown")
#
#     dataframe = get_timeseries_data_as_df(quantum=quantum, entity=oak)
#
#     # delete entity in crate DB
#     quantum.delete_entity(oak.id)
#
#     # delete subscriptions
#     ORION_CB.delete_all_subscriptions()
#
#
#     return dataframe

if __name__ == "__main__":
    print("------EXAMPLE QUANTUM LEAP------")

    setup()

    created_entity = create_entity()

    post_subscription(created_entity.id)

    list_of_subscriptions = get_subscriptions()

    sub_id = notify_ql(list_of_subscriptions, created_entity)

    get_historical_data(created_entity)

    delete_entities_ql(created_entity)

    cleanup_cb(created_entity.id, sub_id)

# TODO: Delete excess code
#     #print(create_example_dataframe())
#
#     # setup logging
#     # before the first initalization the log_config.yaml.example file needs to be
#     modified
#
#     config.setup_logging()
#
#     path_to_config = os.path.join(str(Path().resolve().parent), "config.json")
#
#
#
#     # Reading the config
#     CONFIG = config.Config(path_to_config)
#
#     # creating an instance of the ORION context broker
#     ORION_CB = cb.ContextBroker(CONFIG)
#
# #    ORION_CB.fiware_service = None
#
#     # create an example entity
#     oak = create_entity(ORION_CB)
#
#     # create an instance of Quantumleap
#     quantum = ts.QuantumLeapClient(CONFIG)
#
# #    quantum.fiware_service = None
#     """
#     throttling = 0
#     expires = datetime.datetime(2020, 12, 24, 18).isoformat()
#     notify_url = "http://quantumleap:8668/v2/notify"
#     subscription = quantum.create_subscription_object(oak, notify_url,
#                                 throttling=throttling, expires=expires,)
#
#     # add metadata to include the modification time of the attributes
#     # in the notification
#     subscription.notification.metadata = ["dateCreated", "dateModified"]
#
#     # create subscription in Context Broker
#     print(subscription.get_json())
#
#     sub_id = ORION_CB.create_subscription(subscription.get_json())
#     """
#
#      # create a subscription and register it with the Orion Context Broker
#     notify_url = "http://quantumleap:8668/v2/notify"
#     sub_id = create_subscription(ORION_CB, quantum, oak, notify_url)
#     print("subscription created, id is: " + str(sub_id))
#     print(ORION_CB.get_subscription(sub_id))
#
#     subscription_list = ORION_CB.get_subscription_list()
#     print(subscription_list)
#
#
#     # test update attributes
#     # once with the function and once directly with the Context Broker
#     update_attribute(orion_cb=ORION_CB, entity=oak, attribute_name="height")
#     ORION_CB.update_attribute(oak.id, "leaves", "brown")
#
#
#     # query historical data
#     valuesonly = bool(True)
#     params = {"lastN": 10}
#
#     print(quantum.get_health())
#     print(quantum.get_version())
#     print(quantum.get_entity_data(oak.id))
#     print(quantum.get_entity_data(oak.id, "height", params = params))
#     print(quantum.get_timeseries(oak.id, valuesonly=False))
#     print(quantum.get_entity_data(oak.id, "height", valuesonly))
#     print(quantum.get_entity_type_data("Tree", "height"))
#     print(quantum.get_entity_type_data("Tree", "height", valuesonly))
#
#     """
#     These functions return an internal server error, but are documented as
#     "To Be Implemented" in QuantumLeap API:
#     https://app.swaggerhub.com/apis/smartsdk/ngsi-tsdb/0.2#/
#
#         print(quantum.get_entity_type_data("Tree"))
#         print(quantum.get_entity_type_data("Tree", values_only))
#         print(quantum.get_attributes("height"))
#         print(quantum.get_attributes("height", values_only))
#     """
#
#     dataframe = get_timeseries_data_as_df(quantum=quantum, entity=oak)
#     print(dataframe)
#
#
#
#     # delete entity in orion
#     timeout = 3
#     print("deleting test entity in " + str(timeout) + " seconds")
#     for j in range(0, timeout):
#         time.sleep(1)
#         print("...")
#
#
#
#     print(dataframe)
#     ORION_CB.delete(oak.id)
#
#     # delete entity in crate DB
#     quantum.delete_entity(oak.id)
#
#     # delete subscription, so that the entity is not posted several times
#     # by multiple subscriptions
#     #
#     ORION_CB.delete_subscription(sub_id)
#
#     ORION_CB.delete_all_subscriptions()
