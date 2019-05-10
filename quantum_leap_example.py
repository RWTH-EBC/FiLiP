from filip import orion, config, subscription as sub
import filip.timeseries as ts
import time

def create_entity(orion_cb):
    attr1 = orion.Attribute('height', 10, 'Integer')
    attr2 = orion.Attribute('leaves', 'green', 'String')
    attr3 = orion.Attribute('age', 7.5, 'Float')
    oak = orion.Entity('Oak_Nr_43', 'Tree', [attr1, attr2, attr3])

    orion_cb.post_entity(oak)
    return oak

if __name__=="__main__":
    CONFIG = config.Config()
    ORION_CB = orion.Orion(CONFIG)

    oak = create_entity(ORION_CB)
    quantum = ts.QuantumLeap()
    subscription = quantum.create_subscription_object(oak, "http://localhost:8668/v2/notify")
    sub_id = ORION_CB.create_subscription(subscription.get_json())
    print("subscription created, id is: " + str(sub_id))

    # update entity attributes
    for i in range(0,3):
        ORION_CB.update_attribute(oak.id, "height", (i*3))
        time.sleep(1)

    ORION_CB.update_attribute(oak.id, "leaves", "brown")


    timeout = 4
    print("deleting test entity in " + str(timeout) + " seconds")
    for j in range(0, timeout):
        time.sleep(1)
        print("...")

    ORION_CB.delete(oak.id)
        
