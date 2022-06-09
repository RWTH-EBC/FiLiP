"""
Filter functions to keep client code clean and easy to use.
"""
from typing import List
from filip.clients.ngsi_v2 import ContextBrokerClient
from filip.models import FiwareHeader
from filip.models.ngsi_v2.subscriptions import Subscription


def filter_subscriptions_by_entity(entity_id: str,
                                   entity_type: str,
                                   url: str = None,
                                   fiware_header: FiwareHeader = None,
                                   subscriptions: List[Subscription] = None,
                                   ) -> List[Subscription]:
    """
    Function that filters subscriptions based on the entity id or id pattern
    and entity type or type pattern. The function can be used in two ways,
    wither pass list of subscriptions to filter based on entity or directly pass
    client information to filter subscriptions in a single request.
    Args:
        entity_id: Id of the entity to be matched
        entity_type: Type of the entity to be matched
        url: Url of the context broker service
        fiware_header: Fiware header of the tenant
        subscriptions: List of subscriptions to filter
    Returns:
        list of subscriptions by entity
    """
    if not subscriptions:
        client = ContextBrokerClient(url=url, fiware_header=fiware_header)
        subscriptions = client.get_subscription_list()
    filtered_subscriptions = []
    for subscription in subscriptions:
        for entity in subscription.subject.entities:
            if entity.id == entity_id or (
                    entity.idPattern is not None
                    and entity.idPattern.match(entity_id)):
                if entity.type == entity_type or \
                        (entity.typePattern is not None and
                         entity.typePattern.match(entity_type)):
                    filtered_subscriptions.append(subscription)
    return filtered_subscriptions
