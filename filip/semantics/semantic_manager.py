import ast
import copy
import json
import logging
from enum import Enum
from typing import Optional, Dict, TYPE_CHECKING, Type, List, Any, Union, Set

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
    Command, DeviceAttributeField, DeviceAttribute, DeviceField, DeviceSettings

logger = logging.getLogger('semantics')


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
    """List of all identifiers that were deleted"""

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

        if instance.old_state.state is not None:
            self._deleted_identifiers.append(identifier)

        del self._registry[identifier]

    def instance_was_deleted(self, identifier: InstanceIdentifier) -> bool:
        """
        Check if an instance was deleted

        Args:
            identifier (InstanceIdentifier): Identifier of instance to check

        Returns:
            bool
        """
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
        """
        Get all identifiers that were deleted by the user

        Returns:
            List[InstanceIdentifier]
        """
        return self._deleted_identifiers

    def save(self) -> str:
        """
        Save the state of the registry out of a json string.

        Returns:
             str, json string of registry state
        """
        res = {'instances': [], 'deleted_identifiers': []}

        for identifier, instance in self._registry.items():
            old_state = None
            if instance.old_state.state is not None:
                old_state = instance.old_state.state.json()
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
        """Clear the local state"""
        self._registry.clear()
        self._deleted_identifiers.clear()

    def load(self, json_string: str, semantic_manager: 'SemanticManager'):
        """
        Load the state of the registry out of a json string. The current
        state will be discarded

        Args:
            json_string (str): State expressed as json string
            semantic_manager (SemanticManager): manager to which registry
                belongs
        Returns:
             None
        """
        self.clear()

        save = json.loads(json_string)
        for instance_dict in save['instances']:
            entity_json = instance_dict['entity']
            header = InstanceHeader.parse_raw(instance_dict['header'])

            context_entity = ContextEntity.parse_raw(entity_json)

            instance = semantic_manager._context_entity_to_semantic_class(
                context_entity, header)

            instance.old_state.state = instance_dict['old_state']

            self._registry[instance.get_identifier()] = instance

        for identifier in save['deleted_identifiers']:
            self._deleted_identifiers.append(identifier)


class SemanticManager(BaseModel):
    """
    The Semantic Manager is a static unique object that is delivered with
    each vocabulary model export.

    It provides the interface to interact with the local state and Fiware
    """

    instance_registry: InstanceRegistry
    """Registry managing the local state"""
    class_catalogue: Dict[str, type] = {}
    """Register of class names to classes"""
    datatype_catalogue: Dict[str, Dict[str, str]] = {}
    """Register of datatype names to Dict representation of datatypes"""
    individual_catalogue: Dict[str, type] = {}
    """Register of individual names to their classes"""

    default_header: InstanceHeader = InstanceHeader()

    @staticmethod
    def get_client(instance_header: InstanceHeader) \
            -> ContextBrokerClient:
        """Get the correct ContextBrokerClient to be used with the given header

        Args:
            instance_header (InstanceHeader): Header to be used with client
        Returns:
            ContextBrokerClient
        """
        if instance_header.fiware_version == NgsiVersion.v2:
            return ContextBrokerClient(
                url=instance_header.cb_url,
                fiware_header=instance_header.get_fiware_header())
        else:
            # todo LD
            raise Exception("FiwareVersion not yet supported")

    @staticmethod
    def get_iota_client(instance_header: InstanceHeader) -> IoTAClient:
        """Get the correct IotaClient to be used with the given header

        Args:
            instance_header (InstanceHeader): Header to be used with client
        Returns:
            IoTAClient
        """
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
            header: InstanceHeader) -> SemanticClass:

        """Converts a ContextEntity to a SemanticClass

        Args:
            entity (ContextEntity): entity to convert
            header (InstanceHeader): Header of the new instance

        Returns:
            SemanticClass or SemanticDeviceClass
        """

        class_name = entity.type

        class_: Type = self.get_class_by_name(class_name)

        if not self.is_class_name_an_device_class(class_name):

            loaded_class: SemanticClass = class_(id=entity.id,
                                                 fiware_header=header,
                                                 enforce_new=True)
        else:
            loaded_class: SemanticDeviceClass = class_(id=entity.id,
                                                       fiware_header=header,
                                                       enforce_new=True)
        loaded_class.old_state.state = entity

        # todo catch if Fiware contains more fields than the model has?

        # load values of class from the context_entity into the instance
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
                if isinstance(field, RelationField):
                    # we need to bypass the main setter, as it expects an
                    # instance and we do not want to load the instance if it
                    # is not used
                    field._list.append(converted_value)
                else:
                    field.append(converted_value)

        # load references into instance
        references_attribute = entity.get_attribute("referencedBy")
        references = references_attribute.value

        for identifier_str, prop_list in references.items():
            for prop in prop_list:
                loaded_class.add_reference(
                    InstanceIdentifier.parse_raw(identifier_str), prop)

        # load device_settings into instance, if instance is a device
        if isinstance(loaded_class, SemanticDeviceClass):
            settings_attribute = entity.get_attribute("deviceSettings")
            device_settings = DeviceSettings.parse_obj(settings_attribute.value)

            for key, value in device_settings.dict().items():
                loaded_class.device_settings.__setattr__(key, value)

        return loaded_class

    @staticmethod
    def _convert_value_fitting_for_field(field, value):
        """
        Converts a given value into the correct format for the given field

        Args:
            field: SemanticField
            value: Value to convert

        Returns:
            converted value
        """
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
            # if loading local state, the wrong string delimters are used,
            # and the string is not automatically converted to a dict
            if not isinstance(value, dict):
                value = json.loads(value.replace("'", '"'))

            return Command(name=value['name'])
        elif isinstance(field, DeviceAttributeField):

            # if loading local state, the wrong string delimters are used,
            # and the string is not automatically converted to a dict
            if not isinstance(value, dict):
                value = json.loads(value.replace("'", '"'))

            return DeviceAttribute(
                name=value['name'],
                attribute_type=value[
                    "attribute_type"]
            )

    def get_class_by_name(self, class_name: str) -> Type:
        """
        Get the class object by its type in string form

        Args:
            class_name (str)
        Raises:
            KeyError: if class_name not registered as a SemanticClass

        Returns:
            Type
        """
        return self.class_catalogue[class_name]

    def is_class_name_an_device_class(self, class_name: str) -> bool:
        """
        Test if the name/type of a class belongs to a SemanticDeviceClass

        Args:
            class_name (str): class name to check
        Returns:
            bool, True if belongs to a SemanticDeviceClass
        """
        class_type = self.get_class_by_name(class_name)
        return isinstance(class_type, SemanticDeviceClass)

    def save_state(self, assert_validity: bool = True):
        """
        Save the local state completely to Fiware.

        Args:
            assert_validity (bool): It true an error is raised if the
            RuleFields of one instance are invalid

        Raises:
            AssertionError: If a device endpoint or transport is not defined

        Returns:
            None
        """

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

            client = self.get_client(instance_header=identifier.header)
            try:
                client.delete_entity(entity_id=identifier.id,
                                     entity_type=identifier.type,
                                     delete_devices=True)
            except requests.RequestException:
                pass

            client.close()

        # merge with live state
        for instance in self.instance_registry.get_all():
            if not isinstance(instance, SemanticDeviceClass):
                self.merge_local_and_live_instance_state(instance)

        # save, patch all local instances
        for instance in self.instance_registry.get_all():
            if not isinstance(instance, SemanticDeviceClass):
                client = self.get_client(instance_header=instance.header)
                # it is important that we patch the values else the
                # references field would reach an invalid state if we worked
                # in parallel on an instance
                client.patch_entity(instance.build_context_entity(),
                                    instance.old_state.state)
                client.close()
            else:
                client = self.get_iota_client(instance_header=instance.header)
                # todo : Not propper as we lose state info, patch_device needs
                #  to be implemented
                try:
                    client.delete_device(device_id=instance.id)
                except:
                    pass

                client.post_device(device=instance.build_context_device())
                client.close()

        # update old_state
        for instance in self.instance_registry.get_all():
            instance.old_state.state = instance.build_context_entity()

    def load_instance(self, identifier: InstanceIdentifier) -> SemanticClass:
        """
        Get the instance with the given identifier. It is either loaded from
        local state or retrieved from fiware

        Args:
            identifier (InstanceIdentifier): Identifier to load

        Returns:
            SemanticClass
        """

        if self.instance_registry.contains(identifier=identifier):
            return self.instance_registry.get(identifier=identifier)
        else:
            client = self.get_client(identifier.header)

            entity = client.get_entity(entity_id=identifier.id,
                                       entity_type=identifier.type)
            client.close()

            logger.info(f"Instance ({identifier.id}, {identifier.type}) "
                        f"loaded from Fiware({identifier.header.cb_url}"
                        f", {identifier.header.service}"
                        f"{identifier.header.service_path})")
            return self._context_entity_to_semantic_class(
                entity=entity,
                header=identifier.header)

    def does_instance_exists(self, identifier: InstanceIdentifier) -> bool:
        """
        Check if an instance with the given identifier already exists in
        local state or in Fiware

        Args:
            identifier (InstanceIdentifier): Identifier to check

        Returns:
            bool, true if exists
        """

        if self.instance_registry.contains(identifier=identifier):
            return True
        elif self.was_instance_deleted(identifier):
            return False
        else:
            client = self.get_client(identifier.header)
            return client.does_entity_exists(entity_id=identifier.id,
                                             entity_type=identifier.type)

    def was_instance_deleted(self, identifier: InstanceIdentifier) -> bool:
        """
        Check if the instance with the given identifier was deleted.

        Args:
            identifier (InstanceIdentifier): Identifier to check

        Returns:
            bool, true if deleted
        """
        return self.instance_registry.instance_was_deleted(identifier)

    def get_instance(self, identifier: InstanceIdentifier) -> SemanticClass:
        """
        Get the instance with the given identifier. It is either loaded from
        local state or retrieved from fiware

        Args:
            identifier (InstanceIdentifier): Identifier to load

        Returns:
            SemanticClass
        """
        return self.load_instance(identifier)

    def get_all_local_instances(self) -> List[SemanticClass]:
        """
        Retrieve all SemanticClass instances in the local state

        Returns:
            List[SemanticClass]
        """
        return self.instance_registry.get_all()

    def get_all_local_instances_of_class(self, class_: type, class_name: str) \
            -> List[SemanticClass]:
        """
        Retrieve all instances of a SemanitcClass from Local Storage

        Args:
            class_ (type): Type of classes to retrieve
            class_name (Str): Type of classes to retrieve as string

        Raises:
            AssertionError: If both parameters are non None

        Returns:
            List[SemanticClass]
        """

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
            cb_url: str,
            iota_url: str,
            entity_types: Optional[List[str]] = None,
            entity_ids: Optional[List[str]] = None
    ) -> List[SemanticClass]:
        """
        Loads the instances of given types or ids from Fiware into the local
        state and returns the loaded instances

        Args:
            fiware_header (FiwareHeader): Fiware location to load
            fiware_version (NgsiVersion): Used fiware version
            cb_url (str): URL of the ContextBroker
            iota_url (str): URL of the IotaBroker
            entity_types (Optional[str]): List of the entities types that
                should be loaded
            entity_ids (Optional[str]): List of the entities ids that
                should be loaded

        Raises:
           ValueError: if both entity_types and entity_ids are given
           ValueError: if Retrival of Context-entities fails
        Returns:
             List[SemanticClass]
        """

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

    def get_entity_from_fiware(self, instance_identifier: InstanceIdentifier) \
            -> ContextEntity:
        """
        Retrieve the current entry of an instance in Fiware

        Args:
            instance_identifier (InstanceIdentifier): Identifier to load

        Raises:
            Exception, if Entity is not present

        Returns:
              ContextEntity
        """
        client = self.get_client(instance_identifier.header)

        return client.get_entity(entity_id=instance_identifier.id,
                                 entity_type=instance_identifier.type)

    def load_instances(
            self,
            identifiers: List[InstanceIdentifier]) -> List[SemanticClass]:
        """
        Load all instances, if no local state of it exists it will get taken
        from Fiware and registered locally

        Args:
            identifiers List[InstanceIdentifier]: Identifiers of instances
                that should be loaded
        Raises:
            Exception, if one Entity is not present

        Returns:
           List[SemanticClass]
        """

        return [self.load_instance(iden) for iden in identifiers]

    def set_default_header(self, header: InstanceHeader):
        """
        Set the default header, which all new instance that does not specify a
        header in the constructor receives

        Args:
            header (InstanceHeader): new default header

        Returns:
            None
        """
        self.default_header = copy.deepcopy(header)

    def get_default_header(self) -> InstanceHeader:
        """
        Instance header is read-only, therefore giving back a copy is
        theoretically not needed, but it is cleaner that all instance has an
        own header object that is not shared
        """
        return copy.deepcopy(self.default_header)

    def get_datatype(self, datatype_name: str) -> Datatype:
        """
        Get a Datatype object with the name as key as specified in the model

        Args:
            datatype_name (str): key label of the datatype

        Returns:
            Datatype
        """
        return Datatype.parse_obj(self.datatype_catalogue[datatype_name])

    def get_individual(self, individual_name: str) -> SemanticIndividual:
        """
        Get an individual by its name

        Args:
            individual_name (str)
        Raises:
            KeyError, if name not registered
        Returns:
            SemanticIndividual
        """
        return self.individual_catalogue[individual_name]()

    def save_local_state_as_json(self) -> str:
        """
        Save the local state with all made changes as json string

        Returns:
            Json String, containing all information about the local state
        """
        return self.instance_registry.save()

    def load_local_state_from_json(self, json: str):
        """
        Loads the local state from a json string. The current local state gets
        discarded

        Raises:
            Error, if not a correct json string

        """
        self.instance_registry.load(json, self)

    def visualise_local_state(self):
        """
        Visualise all instances in the local state in a network graph that
        shows which instances reference each other over which fields

        On execution of the methode a temporary image file is created and
        automatically displayed in the standard image viewing software of the
        system
        """
        import igraph
        g = igraph.Graph(directed=True)

        for instance in self.get_all_local_instances():
            g.add_vertex(name=instance.id,
                         label=f"\n\n\n {instance.get_type()} \n {instance.id}",
                         color="green")

        for individual in [self.get_individual(name) for name in
                           self.individual_catalogue]:
            g.add_vertex(label=f"\n\n\n{individual.get_name()}",
                         name=individual.get_name(),
                         color="blue")

        for instance in self.get_all_local_instances():
            for field in instance.get_relation_fields():
                for linked in field.get_all():
                    if isinstance(linked, SemanticClass):
                        g.add_edge(instance.id, linked.id, name=field.name)
                        # g.es[-1]["name"] = field.name

                    elif isinstance(linked, SemanticIndividual):
                        g.add_edge(instance.id, linked.get_name())

        layout = g.layout("fr")
        visual_style = {"vertex_size": 20,
                        "vertex_color": g.vs["color"],
                        "vertex_label": g.vs["label"],
                        "edge_label": g.es["name"],
                        "layout": layout,
                        "bbox": (len(g.vs) * 100, len(g.vs) * 100)}

        igraph.plot(g, **visual_style)

    def merge_local_and_live_instance_state(self, instance: SemanticClass):

        def converted_attribute_values(field, attribute) -> Set:
            return {self._convert_value_fitting_for_field(field, value) for
                    value in attribute.value}

        def _get_added_and_removed_values(
                old_values: Union[List, Set, Any],
                current_values: Union[List, Set, Any]) -> (Set, Set):

            old_set = set(old_values)
            current_set = set(current_values)
            added_values = set()
            removed_values = set()

            # remove deleted values from live state, it can be that the value
            # was also deleted in the live state
            for value in old_set:
                if value not in current_set:
                    removed_values.add(value)

            # add added values
            for value in current_set:
                if value not in old_set:
                    added_values.add(value)

            return added_values, removed_values

        # instance is new. Save it as is
        client = self.get_client(instance.header)
        if not client.does_entity_exists(entity_id=instance.id,
                                         entity_type=instance.get_type()):
            return

        client = self.get_client(instance.header)
        live_entity = client.get_entity(entity_id=instance.id,
                                        entity_type=instance.get_type())
        client.close()

        current_entity = instance.build_context_entity()
        old_entity = instance.old_state.state

        # instance exists already, add all locally added and delete all
        # locally deleted values to the/from the live_state
        for field in instance.get_rule_fields():
            # live_values = set(live_entity.get_attribute(field.name).value)
            live_values = converted_attribute_values(
                field, live_entity.get_attribute(field.name))
            old_values = converted_attribute_values(
                field, old_entity.get_attribute(field.name))
            current_values = converted_attribute_values(
                field, current_entity.get_attribute(field.name))

            (added_values, deleted_values) = \
                _get_added_and_removed_values(
                    old_values, current_values
                    # old_entity.get_attribute(field.name).value,
                    # current_entity.get_attribute(field.name).value
                )

            for value in added_values:
                live_values.add(value)
            for value in deleted_values:
                if value in live_values:
                    live_values.remove(value)

            new_values = list(live_values)
            # update local stated with merged result
            field._list.clear()  # very important to not use field.clear,
                                 # as that methode would also delete values
                                 # in other instances
            for value in new_values:
                converted_value = self._convert_value_fitting_for_field(
                    field, value)
                if isinstance(field, RelationField):
                    # we need to bypass the main setter, as it expects an
                    # instance and we do not want to load the instance if it
                    # is not used
                    field._list.append(converted_value)
                else:
                    field._list.append(converted_value)

        # merge references
        merged_references: Dict = live_entity.get_attribute(
            "referencedBy").value
        current_references: Dict = current_entity.get_attribute(
            "referencedBy").value
        old_references: Dict = old_entity.get_attribute(
            "referencedBy").value

        keys = list(current_references.keys())
        keys.extend(list(old_references.keys()))

        for key in keys:
            current_values = []
            old_values = []
            if key in current_references:
                current_values = current_references[key]
            if key in old_references:
                old_values = old_references[key]

            (added_values, deleted_values) = _get_added_and_removed_values(
                current_values=current_values, old_values=old_values)

            # ensure the merged state has each key
            if key not in merged_references.keys():
                merged_references[key] = []

            # add, added values that did not exist before
            for value in added_values:
                if value not in merged_references[key]:
                    merged_references[key].append(value)

            # delete deleted values if they were not already deleted
            for value in deleted_values:
                if value in merged_references[key]:
                    merged_references[key].remove(value)

            # delete all keys that point to empty lists
            keys_to_delete = []
            for key, value in merged_references.items():
                if len(value) == 0:
                    keys_to_delete.append(key)
            for key in keys_to_delete:
                del merged_references[key]

        # save merged references
        instance.references.clear()
        for key, value in merged_references.items():
            instance.references[InstanceIdentifier.parse_raw(key)] = value

            