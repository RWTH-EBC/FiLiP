from filip import orion, config, subscription as sub
import filip.timeseries as ts
import time, datetime

def create_entity(orion_cb):
    attr1 = orion.Attribute('height', 10, 'Integer')
    attr2 = orion.Attribute('leaves', 'green', 'String')
    attr3 = orion.Attribute('age', 7.5, 'Float')
    oak = orion.Entity('Oak_Nr_44', 'Tree', [attr1, attr2, attr3])

    orion_cb.post_entity(oak)
    return oak

if __name__=="__main__":
    CONFIG = config.Config()
    ORION_CB = orion.Orion(CONFIG)

#    ORION_CB.fiware_service = None
    oak = create_entity(ORION_CB)
    quantum = ts.QuantumLeap(CONFIG)

#    quantum.fiware_service = None

    throttling = 0
    expires = datetime.datetime(2019, 12, 24, 18).isoformat()
    subscription = quantum.create_subscription_object(oak, throttling=throttling,
                                                      expires=expires)

    # add metadata to include the modification time of the attributes
    # in the notification
    subscription.notification.metadata = ["dateCreated", "dateModified"]

    # create subscription in Context Broker
    sub_id = ORION_CB.create_subscription(subscription.get_json())
    print("subscription created, id is: " + str(sub_id))
    print(ORION_CB.get_subscription(sub_id))

    subscription_list = ORION_CB.get_subscription_list()
    print(subscription_list)

    print("updating entity attributes..")
    for i in range(0,10):
        ORION_CB.update_attribute(oak.id, "height", (i*3))
        time.sleep(1)

#    ORION_CB.update_attribute(oak.id, "leaves", "brown")

    # query historical data
    valuesonly = bool(True)
    params = {"lastN": 10}

    print(quantum.get_health())
    print(quantum.get_version())
    print(quantum.get_entity_data(oak.id))
    print(quantum.get_entity_data(oak.id, "height", params = params))
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
    # delete entity in orion
    timeout = 3
    print("deleting test entity in " + str(timeout) + " seconds")
    for j in range(0, timeout):
        time.sleep(1)
        print("...")

    ORION_CB.delete(oak.id)
 
    # delete entity in crate DB
    quantum.delete_entity(oak.id)

    # delete subscription, so that the entity is not posted several times
    # by multiple subscriptions
    ORION_CB.delete_subscription(sub_id)

#    ORION_CB.delete_all_subscriptions()
