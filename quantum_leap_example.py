from filip import orion, config, subscription as sub, utils
import filip.timeseries as ts
import time, datetime
import streamlit as st
import pandas as pd
import streamlit as st
import pandas as pd

def create_entity(orion_cb):
    """
    Function creates a test entity and registers it with the context broker
    :param orion_cb: A Orion Context Broker Instance
    :return: An NGSI Entity object
    """
    oak = {"id": "Oak_nr_44",
           "type": "Tree",
           "height": {"value" : 11,
                      "type" : "Integer" },
           "age": {"value": 7.5,
                   "type": "Float"},
           "leaves": {"value": "green",
                      "type": "String"},
           }
    oak_entity = orion.Entity(oak)

    orion_cb.post_json(oak_entity.get_json())
    return oak_entity

def create_subscription(orion_cb:object, quantum:object, entity:object,
                        notify_url:str, throttinling=0,
                        expires:object =datetime.datetime(2020, 12, 24, 18).isoformat() ,
                        metadata:list=["dateCreated", "dateModified"] ):
    """
    Function creates a test subscription
    :param orion_cb: An instance of the Context Broker, where the subscriptions is registered
    :param quantum: An instance of Quantumleap to manage timeseries data
    :param entity: the entity for which the subscription should be registered
    :param notify_url: ne url which should be notified, if the context broker registers any change in the entity attributes
    :param throttinling: defines the rate at which changes are sampled, e,g. every 5 seconds
    :param expires:  How long the subscription is valid
    :param metadata: add metadate to include when the attribute was changed
    :return: a subscription_id
    """


    subscription =quantum.create_subscription_object(entity, notify_url,
                                       throttinling=throttinling,
                                       expires=expires)
    subscription.notification.metadata = metadata
    sub_id = orion_cb.create_subscription(subscription.get_json())
    return sub_id

def update_attribute(orion_cb:object, entity:object, attribute_name:str):
    # ToDO: Add attribute change for string attributes
    """
    :param orion_cb: And instance of the orion context broker
    :param entity:
    :param attribute_name:
    :return:
    """
    for i in range(0,10):
            value = i*3
            print("new 'height' value: " + str(value))
            orion_cb.update_attribute(entity.id, attribute_name, value)
            time.sleep(1)


def get_timeseries_data_as_df(quantum:object, entity:object, attribute:str=None):
    """

    :param quantum: An instance of quantumleap where the timeseries data should be obtained from
    :param entity:  The entity of which the data should be obtained
    :param attribute: The attribute of which the data should be obtained, if none given, the attributes of all data is obtained
    :return: dataframe
    """
    if attribute:
        ts_dict = quantum.get_timeseries(entity.id, attribute)
    else:
        ts_dict = quantum.get_timeseries(entity.id)
    dataframe = utils.timeseries_to_pandas(ts_dict)
    return dataframe


def create_example_dataframe():
    """
    This is a helper function to display a example for plot_timeseries.py
    :return: a dataframe
    """
    CONFIG = config.Config()
    ORION_CB = orion.Orion(CONFIG)
    oak = create_entity(ORION_CB)
    quantum = ts.QuantumLeap(CONFIG)
    """
    Function creates a test entity and registers it with the context broker 
    :param orion_cb: A Orion Context Broker Instance
    :return: An NGSI Entity object
    """
    oak = {"id": "Oak_nr_44",
           "type": "Tree",
           "height": {"value" : 11,
                      "type" : "Integer" },
           "age": {"value": 7.5,
                   "type": "Float"},
           "leaves": {"value": "green",
                      "type": "String"},
           }
    oak_entity = orion.Entity(oak)

    orion_cb.post_json(oak_entity.get_json())
    return oak_entity

def create_subscription(orion_cb:object, quantum:object, entity:object,
                        notify_url:str, throttinling=0,
                        expires:object =datetime.datetime(2020, 12, 24, 18).isoformat() ,
                        metadata:list=["dateCreated", "dateModified"] ):
    """
    Function creates a test subscription
    :param orion_cb: An instance of the Context Broker, where the subscriptions is registered
    :param quantum: An instance of Quantumleap to manage timeseries data
    :param entity: the entity for which the subscription should be registered
    :param notify_url: ne url which should be notified, if the context broker registers any change in the entity attributes
    :param throttinling: defines the rate at which changes are sampled, e,g. every 5 seconds
    :param expires:  How long the subscription is valid
    :param metadata: add metadate to include when the attribute was changed
    :return: a subscription_id
    """


    subscription =quantum.create_subscription_object(entity, notify_url,
                                       throttinling=throttinling,
                                       expires=expires)
    subscription.notification.metadata = metadata
    sub_id = orion_cb.create_subscription(subscription.get_json())
    return sub_id

def update_attribute(orion_cb:object, entity:object, attribute_name:str):
    # ToDO: Add attribute change for string attributes
    """
    :param orion_cb: And instance of the orion context broker
    :param entity:
    :param attribute_name:
    :return:
    """
    for i in range(0,10):
            value = i*3
            print("new 'height' value: " + str(value))
            orion_cb.update_attribute(entity.id, attribute_name, value)
            time.sleep(1)


def get_timeseries_data_as_df(quantum:object, entity:object, attribute:str=None):
    """

    :param quantum: An instance of quantumleap where the timeseries data should be obtained from
    :param entity:  The entity of which the data should be obtained
    :param attribute: The attribute of which the data should be obtained, if none given, the attributes of all data is obtained
    :return: dataframe
    """
    if attribute:
        ts_dict = quantum.get_timeseries(entity.id, attribute)
    else:
        ts_dict = quantum.get_timeseries(entity.id)
    dataframe = utils.timeseries_to_pandas(ts_dict)
    return dataframe


def create_example_dataframe():
    """
    This is a helper function to display a example for plot_timeseries.py
    :return: a dataframe
    """
    CONFIG = config.Config()
    ORION_CB = orion.Orion(CONFIG)
    oak = create_entity(ORION_CB)
    quantum = ts.QuantumLeap(CONFIG)

    notify_url =  "http://quantumleap:8668/v2/notify"

    sub_id = create_subscription(orion_cb=ORION_CB, quantum=quantum, entity=oak, notify_url=notify_url)

    update_attribute(orion_cb=ORION_CB, entity=oak, attribute_name="height")

    ORION_CB.update_attribute(oak.id, "leaves", "brown")

    dataframe = get_timeseries_data_as_df(quantum=quantum, entity=oak)

    # delete entity in crate DB
    quantum.delete_entity(oak.id)

    # delete subscriptions
    ORION_CB.delete_all_subscriptions()


    return dataframe

if __name__=="__main__":
    #print(create_example_dataframe())

    # setup logging
    # before the first initalization the log_config.yaml.example file needs to be modified

    config.setup_logging()




    # Reading the config
    CONFIG = config.Config()

    # creating an instance of the ORION context broker
    ORION_CB = orion.Orion(CONFIG)

#    ORION_CB.fiware_service = None

    # create an example entity
    oak = create_entity(ORION_CB)

    # create an instance of Quantumleap
    quantum = ts.QuantumLeap(CONFIG)

#    quantum.fiware_service = None
    """ 
    throttling = 0
    expires = datetime.datetime(2020, 12, 24, 18).isoformat()
    notify_url = "http://quantumleap:8668/v2/notify"
    subscription = quantum.create_subscription_object(oak, notify_url,
                                throttling=throttling, expires=expires,)

    # add metadata to include the modification time of the attributes
    # in the notification
    subscription.notification.metadata = ["dateCreated", "dateModified"]

    # create subscription in Context Broker
    print(subscription.get_json())
    
    sub_id = ORION_CB.create_subscription(subscription.get_json())
    """

     # create a subscription and register it with the Orion Context Broker
    notify_url = "http://quantumleap:8668/v2/notify"
    sub_id = create_subscription(ORION_CB, quantum, oak, notify_url)
    print("subscription created, id is: " + str(sub_id))
    print(ORION_CB.get_subscription(sub_id))

    subscription_list = ORION_CB.get_subscription_list()
    print(subscription_list)


    # test update attributes
    # once with the function and once directly with the Context Broker
    update_attribute(orion_cb=ORION_CB, entity=oak, attribute_name="height")
    ORION_CB.update_attribute(oak.id, "leaves", "brown")


    # query historical data
    valuesonly = bool(True)
    params = {"lastN": 10}

    print(quantum.get_health())
    print(quantum.get_version())
    print(quantum.get_entity_data(oak.id))
    print(quantum.get_entity_data(oak.id, "height", params = params))
    print(quantum.get_timeseries(oak.id))
    print(quantum.get_entity_data(oak.id, "height", valuesonly))
    print(quantum.get_entity_type_data("Tree", "height"))
    print(quantum.get_entity_type_data("Tree", "height", valuesonly))

    """
    These functions return an internal server error, but are documented as
    "To Be Implemented" in QuantumLeap API:
    https://app.swaggerhub.com/apis/smartsdk/ngsi-tsdb/0.2#/

        print(quantum.get_entity_type_data("Tree"))
        print(quantum.get_entity_type_data("Tree", valuesonly))
        print(quantum.get_attributes("height"))
        print(quantum.get_attributes("height", valuesonly))
    """

    dataframe = get_timeseries_data_as_df(quantum=quantum, entity=oak)
    print(dataframe)



    # delete entity in orion
    timeout = 3
    print("deleting test entity in " + str(timeout) + " seconds")
    for j in range(0, timeout):
        time.sleep(1)
        print("...")



    print(dataframe)
    ORION_CB.delete(oak.id)
 
    # delete entity in crate DB
    quantum.delete_entity(oak.id)

    # delete subscription, so that the entity is not posted several times
    # by multiple subscriptions
    #
    ORION_CB.delete_subscription(sub_id)

    ORION_CB.delete_all_subscriptions()

