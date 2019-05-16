import filip.subscription as sub
import filip.orion as orion

class QuantumLeap():
    """
    Creates and returns Subscription object so that it can be edited before the subscription
    is actually created. Takes an entity and URL as only obligatory parameters.
    """
    def create_subscription_object(self, entity: orion.Entity, url : str, **kwargs) -> object:
        subject_entity = sub.Subject_Entity(entity.id, entity.type)
        subject = sub.Subject([subject_entity])
        http_params = sub.HTTP_Params(url)
        notification = sub.Notification(http_params)
        throttling = kwargs.get("throttling")
        expires = kwargs.get("expires")
        description = kwargs.get("description")

        subscription = sub.Subscription(subject, notification, description, expires, throttling)
        return subscription

