import filip.subscription as sub
import filip.config as config
import filip.orion as orion
import datetime
import json


AUTH = ('user', 'pass')

# create new subscription following the API Walkthrough example:
# https://fiware-orion.readthedocs.io/en/master/user/walkthrough_apiv2/index.html#subscriptions
def API_Walkthrough_subscription():
    description = "A subscription to get info about Room1"

    subject_entity = sub.Subject_Entity("Room1", "Room")
    subject_condition = sub.Subject_Condition(["pressure"])
    subject = sub.Subject([subject_entity], subject_condition)

    http_params = sub.HTTP_Params("http://localhost:1028/accumulate")
    notification_attributes = sub.Notification_Attributes("attrs", ["temperature"])
    notification = sub.Notification(http_params, notification_attributes)

    expires = datetime.datetime(2040, 1, 1, 14).isoformat()
    print (expires)
    throttling = 5

    subscription = sub.Subscription(subject, notification, description, expires, throttling)
    return subscription.get_json()


def Step_By_Step_reducing_scope_with_expression():
    description = "Notify me of low stock in Store 001"
    subject_entity = sub.Subject_Entity(".*", "InventoryItem")
    subject_expression = sub.Subject_Expression()
    subject_expression.q = "shelfCount<10;refStore==urn:ngsi-ld:Store:002"
    subject_condition = sub.Subject_Condition(["shelfCount"], subject_expression)
    subject = sub.Subject([subject_entity], subject_condition)
    expression = sub.Subject_Expression()
    http_params = sub.HTTP_Params("http://tutorial:3000/subscription/low-stock-store002")
    notification = sub.Notification(http_params)
    notification.attrsFormat = "keyValues"

    subscription = sub.Subscription(subject, notification, description)
    return subscription.get_json()


def http_custom_subscription():
    description = "A subscription to get info about Room3"

    subject_entity = sub.Subject_Entity("Room3", "Room")
    subject_condition = sub.Subject_Condition(["pressure"])
    subject = sub.Subject([subject_entity], subject_condition)

    http_params = sub.HTTP_Params("http://localhost:1028/accumulate")
    http_params.headers =  {"Content-Type": "text/plain", "X-Auth-Token": "n5u43SunZCGX0AbnD9e8R537eDslLM"}
    http_params.method = "PUT"
    http_params.qs = {"type": "${type}", "id": "${id}"}
    http_params.payload = "The temperature is ${temperature} degrees"
    notification = sub.Notification(http_params)

    subscription = sub.Subscription(subject, notification, description)
    print(subscription.get_json())





if __name__=="__main__":
    CONFIG = config.Config()
    ORION_CB = orion.Orion(CONFIG)

    body = API_Walkthrough_subscription()
    print("---------------------")
    print(body)
    sub_id = ORION_CB.create_subscription(body)
    print("subscription id = " + str(sub_id))

    print("---------------------")
    body = Step_By_Step_reducing_scope_with_expression()
    print(body)
    sub_id = ORION_CB.create_subscription(body)
    print("subscription id = " + str(sub_id))

    print("---------------------")
#    http_custom_subscription()
#    print("---------------------")

