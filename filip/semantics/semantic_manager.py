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

    def _context_entity_to_semantic_class(self,
                                         entity: ContextEntity,
                                         identifier: InstanceIdentifier) \
            -> SemanticClass:

        class_name = entity.type

        class_: Type = self.get_class_by_name(class_name)
        loaded_class: SemanticClass = class_(id=identifier.id,
                              fiware_header=identifier.fiware_header)

        # todo catch if Fiware contains more fields than the model has?
        for field in loaded_class.get_fields():
            field_name = field.name

            entity_attribute = entity.get_attribute(field_name)
            if entity_attribute is None:
                raise Exception(
                    f"The corresponding entity in Fiware misses a field that "
                    f"is required by the class_model: {field_name}. The "
                    f"fiware state and the vocabulary are not compatible")

            entity_field_value = entity.get_attribute(field_name).value
            if isinstance(entity_field_value, List):
                field.extend(entity.get_attribute(field_name).value)
            else:
                field.append(entity.get_attribute(field_name).value)

        return loaded_class

    def get_class_by_name(self, class_name:str) -> Type:
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
            with ContextBrokerClient(fiware_header=identifier.fiware_header) \
                    as client:

                entity = client.get_entity(entity_id=identifier.id,
                                           entity_type=identifier.type)
                return self._context_entity_to_semantic_class(
                    entity=entity,
                    identifier=identifier
                )

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
