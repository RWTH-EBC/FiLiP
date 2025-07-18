"""
In this example, we will demonstrate the best practice to use system attributes: default
meta attributes the LD context broker adds to each entity.
"""

import logging
import time
from datetime import datetime
from filip.clients.ngsi_ld.cb import ContextBrokerLDClient
from filip.models import FiwareLDHeader
from filip.models.ngsi_ld.context import ContextLDEntity, NamedContextProperty
from filip.utils.cleanup import clear_context_broker_ld
from filip.config import settings

# ## Parameters
#
# To run this example you need a working Fiware ld setup with a
# Context Broker. Here you can set the addresses:
#
# Host address of Context Broker
LD_CB_URL = settings.LD_CB_URL

# Here you can also change FIWARE service.
# NGSI-LD Tenant
NGSILD_TENANT = "filip_e15"

# Setting up logging
logging.basicConfig(
    level="INFO",
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    fiware_header = FiwareLDHeader(ngsild_tenant=NGSILD_TENANT)
    cb_ld_client = ContextBrokerLDClient(url=LD_CB_URL, fiware_header=fiware_header)
    try:
        clear_context_broker_ld(cb_ld_client=cb_ld_client)
    except:
        pass
    id = "urn:ngsi-ld:temperatureSensor"
    cb_ld_client.post_entity(
        ContextLDEntity(
            id=id,
            type="TemperatureSensor",
            **{"temperature": {"type": "Property", "value": 50, "unitCode": "CEL"}},
        )
    )

    # The orion ld context broker keeps track of special attributes
    # That can only be created and updated by the broker itself
    # the so called "system attributes" are in fact the time when an
    # entity has been created or last modified(createdAt, modifiedAt)

    entity = cb_ld_client.get_entity(entity_id=id)

    # Without prompting it, the broker will return null for these values
    logger.info(
        f'modifiedAt attribute is {entity.modifiedAt if entity.modifiedAt is not None else "Not provided"}'
    )
    logger.info(
        f'createdAt attribute is {entity.createdAt if entity.createdAt is not None else "Not provided"}'
    )

    # To get the system attributes, one has to provide the sysAttrs options in the parameters
    entity = cb_ld_client.get_entity(entity_id=id, options="sysAttrs")
    old_mod = entity.modifiedAt
    logger.info(f'modifiedAt attribute is {old_mod if old_mod is not None else "None"}')
    logger.info(
        f'createdAt attribute is {entity.createdAt if entity.createdAt is not None else "None"}'
    )

    # And the context broker will update accordingly
    time.sleep(5)
    cb_ld_client.update_entity_attribute(
        entity_id=id,
        attr=NamedContextProperty(name="temperature", value=23),
        attr_name="temperature",
    )

    entity = cb_ld_client.get_entity(entity_id=id, options="sysAttrs")
    new_mod = entity.modifiedAt
    t_delta = datetime.fromisoformat(new_mod.replace("Z", "")) - datetime.fromisoformat(
        old_mod.replace("Z", "")
    )

    logger.info(f"Modified {t_delta.seconds} seconds ago")
    clear_context_broker_ld(cb_ld_client=cb_ld_client)
