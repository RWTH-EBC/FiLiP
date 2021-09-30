from enum import Enum
from typing import Optional, Dict, TYPE_CHECKING, Type, List

from filip.models.ngsi_v2.context import ContextEntity

from filip.clients.ngsi_v2 import ContextBrokerClient

from filip.models import FiwareHeader
from pydantic import BaseModel
from filip.semantics.semantic_models import InstanceRegistry, ClientSetting, \
    InstanceIdentifier, SemanticClass


class SemanticManager(BaseModel):

    instance_registry: InstanceRegistry
    model_catalogue: Dict[str, type] = {}
    client_setting: ClientSetting = ClientSetting.unset

    def load_instance_2(self, identifier: InstanceIdentifier,
                      instance: Optional[SemanticClass] = None):
        if self.client_setting == ClientSetting.v2:
            with ContextBrokerClient(fiware_header=identifier.fiware_header) \
                    as client:

                entity = client.get_entity(entity_id=identifier.id,
                                           entity_type=identifier.type)

                class_name = entity.type

                if instance is not None:
                    loaded_class = instance
                    assert class_name == instance.get_type()
                else:
                    class_: Type = self._get_class_by_name(class_name)
                    loaded_class = class_()

                for field_name in loaded_class:
                    field = loaded_class.get_property(field_name)

                    entity_field_value = entity.get_attribute(field_name).value
                    if isinstance(entity_field_value, List):
                        field.extend(entity.get_attribute(field_name).value)
                    else:
                        field.append(entity.get_attribute(field_name).value)

                return loaded_class


    def _get_class_by_name(self, class_name:str) -> Type:
        return self.model_catalogue[class_name]

    def parse_context_entity_to_semantic_instance(self,
                                               context_entity: ContextEntity):
        pass

    def save_all_instances(self):
        pass

    def load_instance(self, identifier: InstanceIdentifier) -> SemanticClass:
        if self.instance_registry.contains(identifier=identifier):
            return self.instance_registry.get(identifier=identifier)

        elif self.client_setting == ClientSetting.v2:
            assert False

        assert False

    def does_instance_exists(self, identifier: InstanceIdentifier) -> bool:
        if self.instance_registry.contains(
                identifier=identifier):
            return True
        elif self.client_setting == ClientSetting.v2:
            with ContextBrokerClient(fiware_header=identifier.fiware_header) \
                    as client:
                return client.does_entity_exists(entity_id=identifier.id,
                                                 entity_type=identifier.type)

        else:
            return False
