from filip import orion, config, subscription as sub
import time

def create_entity(orion_cb):
    attr1 = orion.Attribute('height', 10, 'Integer')
    attr2 = orion.Attribute('leaves', 'green', 'String')
    attr3 = orion.Attribute('age', 7.5, 'Float')
    oak = orion.Entity('Oak_Nr_43', 'Tree', [attr1, attr2, attr3])

    orion_cb.post_entity(oak)
    return oak

# subscription similar to example in QuantumLeap Manual
# https://smartsdk.github.io/ngsi-timeseries-api/user/
def create_subscription(orion_cb):
    description = "Tree subscription to test quantum leap"
    subject_entity = sub.Subject_Entity(".", "Tree")
    subject_condition = sub.Subject_Condition(["height", "leaves"])
    subject = sub.Subject([subject_entity], subject_condition)

    http_params = sub.HTTP_Params("http://localhost:8668/v2/notify")
    notification_attributes = sub.Notification_Attributes("attrs", ["height", "leaves"])
    notification = sub.Notification(http_params, notification_attributes)
    notification.metadata = ["dateCreated", "dateModified"]
    
    subscription = sub.Subscription(subject, notification, description)
    subscription.throttling = 5

    sub_id = orion_cb.create_subscription(subscription.get_json())
    print("subscription created, id is: " + str(sub_id))



if __name__=="__main__":
    # create entity and subscribe to it
    CONFIG = config.Config()
    ORION_CB = orion.Orion(CONFIG)

    oak = create_entity(ORION_CB)
    create_subscription(ORION_CB)

    # update entity attributes
    for i in range(0,10):
        ORION_CB.update_attribute(oak.id, "height", (i*3))
        time.sleep(1)

    ORION_CB.update_attribute(oak.id, "leaves", "brown")

