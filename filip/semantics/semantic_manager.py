from enum import Enum
from typing import Optional, Dict, TYPE_CHECKING, Type, List

from filip.models.ngsi_v2.context import ContextEntity

from filip.clients.ngsi_v2 import ContextBrokerClient

from filip.models import FiwareHeader
from pydantic import BaseModel
from filip.semantics.semantic_models import InstanceRegistry, ClientSetting, \
    InstanceIdentifier, SemanticClass, InstanceHeader


class SemanticManager(BaseModel):

    instance_registry: InstanceRegistry
    model_catalogue: Dict[str, type] = {}
    client_setting: ClientSetting = ClientSetting.unset

    def _get_client(self, fiware_header: Optional[FiwareHeader] = None):
        if self.client_setting == ClientSetting.v2:
            return ContextBrokerClient(fiware_header=fiware_header)
        else:
            # todo LD
            raise Exception

    def _context_entity_to_semantic_class(self,
                                          entity: ContextEntity,
                                          header: InstanceHeader) \
            -> SemanticClass:

        class_name = entity.type

        class_: Type = self.get_class_by_name(class_name)
        loaded_class: SemanticClass = class_(id=entity.id,
                                             fiware_header=header,
                                             enforce_new=True)

        # todo catch if Fiware contains more fields than the model has?
        for field in loaded_class.get_fields():
            field_name = field.name
            entity_attribute = entity.get_attribute(field_name)
            if entity_attribute is None:
                raise Exception(
                    f"The corresponding entity for ({entity.id},{entity.type}) "
                    f"in Fiware misses a field that "
                    f"is required by the class_model: {field_name}. The "
                    f"fiware state and the used vocabulary models are not "
                    f"compatible")

            entity_field_value = entity.get_attribute(field_name).value

            if isinstance(entity_field_value, List):
                json_list = entity_field_value
            else:
                json_list = [entity_field_value]

            for json in json_list:
                # convert json to Identifier, use Identifier to load_class,
                # give class to field

                identifier = InstanceIdentifier.parse_obj(json)

                class_: SemanticClass = self.load_instance(identifier)
                field.append(class_)

        return loaded_class

    def get_class_by_name(self, class_name:str) -> Type:
        return self.model_catalogue[class_name]

    def save_all_instances(self):

        client = self._get_client()

        for instance in self.instance_registry.get_all():
            client.patch_entity(entity=instance.build_context_entity(),
                                old_entity=instance.old_state)
        client.close()

    def load_instance(self, identifier: InstanceIdentifier) -> SemanticClass:

        if self.instance_registry.contains(identifier=identifier):
            return self.instance_registry.get(identifier=identifier)
        else:
            client = self._get_client()

            entity = client.get_entity(entity_id=identifier.id,
                                       entity_type=identifier.type)
            client.close()
            return self._context_entity_to_semantic_class(
                entity=entity,
                header=identifier.header)

    def does_instance_exists(self, identifier: InstanceIdentifier) -> bool:
        if self.instance_registry.contains(identifier=identifier):
            return True

        client = self._get_client(identifier.header.get_fiware_header())
        return client.does_entity_exists(entity_id=identifier.id,
                                         entity_type=identifier.type)

    def load_instances_from_fiware(
            self,
            fiware_header: FiwareHeader,
            entity_types: Optional[List[str]],
            entity_ids: Optional[List[str]],
            identifiers: Optional[List[InstanceIdentifier]]) \
        -> List[SemanticClass]:

        number_of_filled_params = len([p for p in
                                       [entity_types, entity_ids, identifiers]
                                       if p is not None])
        if number_of_filled_params > 1:
            raise ValueError("Only one search parameter is allowed")

        client = self._get_client(fiware_header=fiware_header)

        if identifiers is None:
            entities = client.get_entity_list(
                entity_ids=entity_ids,
                entity_types=entity_types)
        else:
            entities = \
                [client.get_entity(entity_id=i.id, entity_type=i.type)
                 for i in identifiers]

        header: InstanceHeader = InstanceHeader(service=fiware_header.service,
                            service_path=fiware_header.service_path)
        client.close()
        return [self._context_entity_to_semantic_class(e, header)
                for e in entities]


