"""
# Example explaining context in NGSI-LD , and demonstrating
# The multitenancy of the FIWARE orion ld context broker
"""

import logging

from filip.clients.ngsi_ld.cb import ContextBrokerLDClient
from filip.models.base import FiwareLDHeader, core_context
from filip.models.ngsi_ld.context import ContextLDEntity, NamedContextProperty
from filip.config import settings
from filip.utils.cleanup import clear_context_broker_ld

LD_CB_URL = settings.LD_CB_URL
NGSILD_TENANT = "filip"

# Setting up logging
logging.basicConfig(
    level="INFO",
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
)
logger = logging.getLogger(__name__)


def silent_clear(cb):
    try:
        clear_context_broker_ld(cb_ld_client=cb)
    except:
        pass


if __name__ == "__main__":

    # Context in ld is used to create unique identifiers for entities and their attributes
    # It provides a model definition to third party apps for interoperability
    # https://ngsi-ld-tutorials.readthedocs.io/en/latest/understanding-%40context.html

    # When no context is provided, default is used, which defined by core_context
    logger.info(core_context)

    default_header = FiwareLDHeader(ngsild_tenant=NGSILD_TENANT)
    default_client = ContextBrokerLDClient(fiware_header=default_header, url=LD_CB_URL)

    # A custom context can be provided through a 'Link' http header
    custom_header = FiwareLDHeader(ngsild_tenant=NGSILD_TENANT)

    custom_context = (
        "https://n5geh.github.io/n5geh.test-context.io/context_saref.jsonld"
    )
    custom_header.set_context(custom_context)
    custom_client = ContextBrokerLDClient(fiware_header=custom_header, url=LD_CB_URL)

    silent_clear(custom_client)
    silent_clear(default_client)

    temperature_sensor_dict = {
        "id": "urn:ngsi-ld:temperatureSensor",
        "type": "TemperatureSensor",
        "temperature": {"type": "Property", "value": 23, "unitCode": "CEL"},
    }

    temperature_sensor = ContextLDEntity(**temperature_sensor_dict)

    # Posting the entity to differently contextualized broker clients will clash
    # Because the entity is the same eventually
    default_client.post_entity(entity=temperature_sensor)
    default_entity = default_client.get_entity(entity_id=temperature_sensor.id)
    default_client.delete_entity_by_id(entity_id=temperature_sensor.id)

    custom_client.post_entity(entity=temperature_sensor)
    custom_entity = custom_client.get_entity(entity_id=temperature_sensor.id)
    custom_client.delete_entity_by_id(entity_id=temperature_sensor.id)

    logger.info(default_entity.model_dump(exclude="context"))
    logger.info(custom_entity.model_dump(exclude="context"))

    # However the context , i.e how third party programs might interpret the model is different
    logger.info(default_entity.context)
    logger.info(custom_entity.context)

    # Context can also be provided per single entity
    default_client.post_entity(
        entity=ContextLDEntity(
            context=[
                "https://n5geh.github.io/n5geh.test-context.io/context_saref.jsonld"
            ],
            **temperature_sensor_dict,
        )
    )

    default_entity = default_client.get_entity(entity_id=temperature_sensor.id)
    default_client.delete_entity_by_id(entity_id=temperature_sensor.id)
    logger.info(default_entity.context)
    logger.info(custom_entity.context)

    # To avoid clashes, one might use different tenants
    silent_clear(custom_client)
    custom_header = FiwareLDHeader(ngsild_tenant="customtenant")
    custom_client = ContextBrokerLDClient(url=LD_CB_URL, fiware_header=custom_header)

    # An entity posted to a specific tenant can only be obtained from the same tenant
    default_client.post_entity(entity=temperature_sensor)
    default_entity = default_client.get_entity(entity_id=temperature_sensor.id)
    logger.info(default_entity.model_dump(exclude="context"))

    # And so this will raise
    try:
        custom_client.get_entity(entity_id=temperature_sensor.id)
    except:
        logger.info("Entity does not exist: As expected !")

    # Entities posted to different tenants do not clash
    temperature_sensor.delete_properties(["temperature"])
    temperature_sensor.add_properties(
        [NamedContextProperty(name="temperature", value=50, unitCode="CEL")]
    )

    custom_client.post_entity(entity=temperature_sensor)
    custom_entity = custom_client.get_entity(entity_id=temperature_sensor.id)
    logger.info(custom_entity.model_dump(exclude="context"))

    # And the following will always evaluate to TRUE
    logger.info(default_entity.temperature.value != custom_entity.temperature.value)

    silent_clear(custom_client)
    silent_clear(default_client)
