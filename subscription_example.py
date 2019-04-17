import filip.subscription as sub
import datetime



if __name__=="__main__":
    # create new subscription following the API Walkthrough example:
    # https://fiware-orion.readthedocs.io/en/master/user/walkthrough_apiv2/index.html#subscriptions
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
    print(subscription.get_json())




