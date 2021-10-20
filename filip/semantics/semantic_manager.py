import ast
import copy
import json
from enum import Enum
from typing import Optional, Dict, TYPE_CHECKING, Type, List, Any

import requests
from requests import RequestException

from filip.models.base import NgsiVersion

from filip import settings
from filip.semantics.vocabulary import Individual

from filip.models.ngsi_v2.context import ContextEntity

from filip.clients.ngsi_v2 import ContextBrokerClient, IoTAClient

from filip.models import FiwareHeader
from pydantic import BaseModel
from filip.semantics.semantic_models import \
    InstanceIdentifier, SemanticClass, InstanceHeader, Datatype, DataField, \
    RelationField, SemanticIndividual, SemanticDeviceClass, CommandField, \
    Command, DeviceAttributeField, DeviceAttribute


class InstanceRegistry(BaseModel):
    """
    Holds all the references to the local SemanticClass instances.
    The instance registry is a global object, that is directly inject in the
    SemanticClass constructor over the SemanticManager
    """
    _registry: Dict[InstanceIdentifier, 'SemanticClass'] = {}
    """ Dict of the references to the local SemanticClass instances. 
        Instances are saved with their identifier as key """

    _deleted_identifiers: List[InstanceIdentifier] = []

    def delete(self, instance: 'SemanticClass'):
        """

        Raises:
           KeyError, if identifier unknown
        """
        identifier = instance.get_identifier()
        if not self.contains(identifier):
            raise KeyError(f"Identifier {identifier} unknown, "
                           f"can not delete")

        # If instance was loaded from Fiware it has an old_state.
        # if that is the case, we need to note that we have deleted the instance
        # to delete it on save, and do not load it again from Fiware

        if instance.old_state is not None:
            self._deleted_identifiers.append(identifier)

        del self._registry[identifier]

    def instance_was_deleted(self, identifier: InstanceIdentifier):
        return identifier in self._deleted_identifiers

    def register(self, instance: 'SemanticClass'):
        """
        Register a new instance of a SemanticClass in the registry

        Args:
            instance(SemanticClass):  Instance to be registered
        Raises:
            AttributeError: if Instance is already registered
        """
        identifier = instance.get_identifier()

        if identifier in self._registry:
            raise AttributeError('Instance already exists')
        else:
            self._registry[identifier] = instance

    def get(self, identifier: InstanceIdentifier) -> 'SemanticClass':
        """Retrieve an registered instance with its identifier

        Args:
            identifier(InstanceIdentifier): identifier belonging to instance
        Returns:
            SemanticClass
        """
        return self._registry[identifier]

    def contains(self, identifier: InstanceIdentifier) -> bool:
        """Test if an identifier is registered

        Args:
            identifier(InstanceIdentifier): identifier belonging to instance
        Returns:
            bool, True if registered
        """
        return identifier in self._registry

    def get_all(self) -> List['SemanticClass']:
        """Get all registered instances

        Returns:
            List[SemanticClass]
        """
        return list(self._registry.values())

    def get_all_deleted_identifiers(self) -> List['InstanceIdentifier']:
        return self._deleted_identifiers

    def save(self):
        res = {'instances': [], 'deleted_identifiers': []}

        # todo: old-state, device-settings
        for identifier, instance in self._registry.items():
            print("")
            print(instance.build_context_entity())
            old_state = None
            if instance.old_state is not None:
                old_state = instance.old_state.json()
            instance_dict = {
                "entity": instance.build_context_entity().json(),
                "header": instance.header.json(),
                "old_state": old_state
            }
            res['instances'].append(instance_dict)

        for identifier in self._deleted_identifiers:
            res['deleted_identifiers'].append(identifier.json())

        return json.dumps(res, indent=4)

    def clear(self):
        self._registry.clear()
        self._deleted_identifiers.clear()

    def load(self, json_string: str, semantic_manager: 'SemanticManager'):

        self.clear()

        # print(json_string)

        save = json.loads(json_string)
        for instance_dict in save['instances']:

            entity_json = instance_dict['entity']
            header = InstanceHeader.parse_raw(instance_dict['header'])

            context_entity = ContextEntity.parse_raw(entity_json)
            print("")
            print(context_entity)


            instance = semantic_manager._context_entity_to_semantic_class(
                context_entity, header)




class SemanticManager(BaseModel):

    instance_registry: InstanceRegistry
    class_catalogue: Dict[str, type] = {}
    datatype_catalogue: Dict[str, Dict[str, str]] = {}
    individual_catalogue: Dict[str, type] = {}

    default_header: InstanceHeader = InstanceHeader()

    def get_client(self, instance_header: InstanceHeader):
        if instance_header.fiware_version == NgsiVersion.v2:
            return ContextBrokerClient(
                url=instance_header.cb_url,
                fiware_header=instance_header.get_fiware_header())
        else:
            # todo LD
            raise Exception("FiwareVersion not yet supported")

    def get_iota_client(self, instance_header: InstanceHeader):
        if instance_header.fiware_version == NgsiVersion.v2:
            return IoTAClient(
                url=instance_header.iota_url,
                fiware_header=instance_header.get_fiware_header())
        else:
            # todo LD
            raise Exception("FiwareVersion not yet supported")

    def _context_entity_to_semantic_class(
            self,
            entity: ContextEntity,
            header: InstanceHeader)-> SemanticClass:

        class_name = entity.type

        class_: Type = self.get_class_by_name(class_name)

        if not self.is_class_name_an_device_class(class_name):

            loaded_class: SemanticClass = class_(id=entity.id,
                                                 fiware_header=header,
                                                 old_state=entity,
                                                 enforce_new=True)
        else:
            loaded_class: SemanticDeviceClass = class_(id=entity.id,
                                                       fiware_header=header,
                                                       old_state=entity,
                                                       enforce_new=True)

        # todo catch if Fiware contains more fields than the model has?
        for field in loaded_class.get_fields():
            field.clear()  # remove default values, from hasValue relations
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
                values = entity_field_value
            else:
                values = [entity_field_value]

            for value in values:
                converted_value = self._convert_value_fitting_for_field(
                    field, value)
                field._list.insert(len(field._list), converted_value)


        references_attribute = entity.get_attribute("__references")
        references = references_attribute.value

        for identifier_str, prop_list in references.items():
            for prop in prop_list:
                loaded_class.add_reference(
                    InstanceIdentifier.parse_raw(identifier_str), prop)

        return loaded_class

    def _convert_value_fitting_for_field(self, field, value):
        if isinstance(field, DataField):
            return value
        elif isinstance(field, RelationField):
            # convert json to Identifier, inject identifier in Relation,
            # the class will be hotloaded if the value in the is
            # relationship is accessed

            if not isinstance(value, dict):  # is an individual
                return value
            else:  # is an instance_identifier
                return InstanceIdentifier.parse_obj(value)
        elif isinstance(field, CommandField):
            return Command(name=value['name'])
        elif isinstance(field, DeviceAttributeField):

            print("")
            print(value)
            if not isinstance(value, dict):
                value = json.loads(value.replace("'",'"'))
            return DeviceAttribute(
                                   name=value['name'],
                                   attribute_type=value[
                                       "attribute_type"]
                               )

    def get_class_by_name(self, class_name:str) -> Type:
        return self.class_catalogue[class_name]

    def is_class_name_an_device_class(self, class_name:str) -> bool:
        class_type = self.get_class_by_name(class_name)
        return isinstance(class_type, SemanticDeviceClass)

    def save_state(self, assert_validity: bool = True):

        if assert_validity:
            for instance in self.instance_registry.get_all():
                if isinstance(instance, Individual):
                    continue

                assert instance.are_rule_fields_valid(), \
                    f"Attempted to save the SemanticEntity {instance.id} of " \
                    f"type {instance._get_class_name()} with invalid fields " \
                    f"{[f.name for f in instance.get_invalid_fields()]}. " \
                    f"Local state was not saved"
        for instance in self.instance_registry.get_all():
            if isinstance(instance, SemanticDeviceClass):
                assert instance.device_settings.endpoint is not None, \
                    "Device needs to be given an endpoint. " \
                    "Local state was not saved"
                assert instance.device_settings.transport is not None, \
                    "Device needs to be given a transport setting. " \
                    "Local state was not saved"

        # delete all instance that were loaded from Fiware and then deleted
        # wrap in try, as the entity could have been deleted by a third party
        for identifier in self.instance_registry.get_all_deleted_identifiers():

            # we need to handle devices and normal classes with different
            # clients

            if not self.is_class_name_an_device_class(identifier.type):
                client = self.get_client(instance_header=identifier.header)
                try:
                    client.delete_entity(entity_id=identifier.id,
                                         entity_type=identifier.type)
                except requests.RequestException:
                    pass

                client.close()
            else:
                client = self.get_iota_client(
                    instance_header=identifier.header)
                try:
                    client.delete_device(device_id=identifier.id)
                except requests.RequestException:
                    pass

                client.close()

        # save, patch all local instances
        for instance in self.instance_registry.get_all():
            if not isinstance(instance, SemanticDeviceClass):
                client = self.get_client(instance_header=instance.header)
                client.patch_entity(instance.build_context_entity(),
                                    instance.old_state)
                client.close()
            else:
                client = self.get_iota_client(instance_header=instance.header)
                # todo: Not propper as we lose state info, patch_device needs
                #  to be implemented
                try:
                    client.delete_device(device_id=instance.id)
                except:
                    pass

                client.post_device(device=instance.build_context_device())
                client.close()

        # delete the local state, if new changes are made, the entities are
        # pulled from fiware with new up-to-date states
        # self.instance_registry.clear()


    def load_instance(self, identifier: InstanceIdentifier) -> SemanticClass:

        if self.instance_registry.contains(identifier=identifier):
            return self.instance_registry.get(identifier=identifier)
        else:
            client = self.get_client(identifier.header)

            entity = client.get_entity(entity_id=identifier.id,
                                       entity_type=identifier.type)
            client.close()
            return self._context_entity_to_semantic_class(
                entity=entity,
                header=identifier.header)

    def does_instance_exists(self, identifier: InstanceIdentifier) -> bool:

        if self.instance_registry.contains(identifier=identifier):
            return True
        elif self.was_instance_deleted(identifier):
            return False
        else:
            client = self.get_client(identifier.header)
            return client.does_entity_exists(entity_id=identifier.id,
                                             entity_type=identifier.type)

    def was_instance_deleted(self, identifier: InstanceIdentifier) -> bool:
        return self.instance_registry.instance_was_deleted(identifier)

    def get_instance(self, identifier: InstanceIdentifier) -> SemanticClass:
        return self.load_instance(identifier)

    def get_all_local_instances_of_class(self, class_:type, class_name:str):

        assert class_ is None or class_name is None, \
            "Only one parameter is allowed"
        assert class_ is not None or class_name is not None, \
            "One parameter is required"

        if class_ is not None:
            class_name = class_.__name__

        res = []
        for instance in self.instance_registry.get_all():
            if instance.get_type() == class_name:
                res.append(instance)
        return res

    def load_instances_from_fiware(
            self,
            fiware_header: FiwareHeader,
            fiware_version: NgsiVersion,
            entity_types: Optional[List[str]],
            entity_ids: Optional[List[str]],
            cb_url: str,
            iota_url: str) -> List[SemanticClass]:

        if len([p for p in [entity_types, entity_ids] if p is not None]) > 1:
            raise ValueError("Only one search parameter is allowed")

        header: InstanceHeader = InstanceHeader(
            service=fiware_header.service,
            service_path=fiware_header.service_path,
            cb_url=cb_url,
            iota_url=iota_url,
            fiware_version=fiware_version
        )

        client = self.get_client(header)

        entities = client.get_entity_list(entity_ids=entity_ids,
                                          entity_types=entity_types)
        client.close()

        return [self._context_entity_to_semantic_class(e, header)
                for e in entities]

    def get_entity_from_fiware(self, instance_identifier: InstanceIdentifier)\
            -> ContextEntity:
        client = self.get_client(instance_identifier.header)

        return client.get_entity(entity_id=instance_identifier.id,
                                 entity_type=instance_identifier.type)

    def load_instances(
            self,
            identifiers: Optional[List[InstanceIdentifier]]) \
        -> List[SemanticClass]:
        """
        Load all instances, if no local state of it exists it will get taken
        from Fiware and registered locally
        """

        return [self.load_instance(iden) for iden in identifiers]

    def set_default_header(self, header: InstanceHeader):
        self.default_header = copy.deepcopy(header)

    def get_default_header(self) -> InstanceHeader:
        """
        Instance header is read-only, therefore giving back a copy is
        theoraticaly not needed, but it is cleaner that all instance has an
        own header object that is not shared
        """
        return copy.deepcopy(self.default_header)

    def get_datatype(self, datatype_name: str) -> Datatype:
        return Datatype.parse_obj(self.datatype_catalogue[datatype_name])

    def get_individual(self, individual_name: str) -> SemanticIndividual:
        return self.individual_catalogue[individual_name]()

    def save_local_state_as_json(self) -> str:
        return self.instance_registry.save()

    def load_local_state_from_json(self, json:str):
        self.instance_registry.load(json, self)



