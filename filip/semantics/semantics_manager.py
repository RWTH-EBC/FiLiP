"""Manages the local state of the semantic instances"""

import copy
import json
import logging
import uuid
from math import inf

import requests

from typing import Optional, Dict, Type, List, Any, Union, Set
from pydantic import BaseModel, Field
from rapidfuzz import process

from filip.models.base import NgsiVersion
from filip.models.ngsi_v2.iot import DeviceSettings
from filip.semantics.vocabulary import Individual
from filip.models.ngsi_v2.context import ContextEntity
from filip.clients.ngsi_v2 import ContextBrokerClient, IoTAClient
from filip.models import FiwareHeader
from filip.semantics.semantics_models import \
    InstanceIdentifier, SemanticClass, InstanceHeader, Datatype, DataField, \
    RelationField, SemanticIndividual, SemanticDeviceClass, CommandField, \
    Command, DeviceAttributeField, DeviceAttribute
from filip.utils.simple_ql import QueryString


logger = logging.getLogger('semantics')


class InstanceRegistry(BaseModel):
    """
    Holds all the references to the local SemanticClass instances.
    The instance registry is a global object, that is directly inject in the
    SemanticClass constructor over the SemanticsManager
    """
    _registry: Dict[InstanceIdentifier, 'SemanticClass'] = {}
    """ Dict of the references to the local SemanticClass instances. 
        Instances are saved with their identifier as key """

    _deleted_identifiers: List[InstanceIdentifier] = []
    """List of all identifiers that were deleted"""

    def delete(self, instance: 'SemanticClass'):
        """Delete an instance from the registry

        Args:
            instance(SemanticClass): Instance to remove

        Raises:
           KeyError, if identifier unknown

        Returns:
            None
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
                old_state = instance.old_state.state.model_dump_json()
            instance_dict = {
                "entity": instance.build_context_entity().model_dump_json(),
                "header": instance.header.model_dump_json(),
                "old_state": old_state
            }
            res['instances'].append(instance_dict)

        for identifier in self._deleted_identifiers:
            res['deleted_identifiers'].append(identifier.model_dump_json())

        return json.dumps(res, indent=4)

    def clear(self):
        """Clear the local state"""
        self._registry.clear()
        self._deleted_identifiers.clear()

    def load(self, json_string: str, semantic_manager: 'SemanticsManager'):
        """
        Load the state of the registry out of a json string. The current
        state will be discarded

        Args:
            json_string (str): State expressed as json string
            semantic_manager (SemanticsManager): manager to which registry
                belongs
        Returns:
             None
        """
        self.clear()

        save = json.loads(json_string)
        for instance_dict in save['instances']:
            entity_json = instance_dict['entity']
            header = InstanceHeader.model_validate(instance_dict['header'])

            context_entity = ContextEntity.model_validate(entity_json)

            instance = semantic_manager._context_entity_to_semantic_class(
                context_entity, header)

            if instance_dict['old_state'] is not None:
                instance.old_state.state = \
                    ContextEntity.model_validate(instance_dict['old_state'])

            self._registry[instance.get_identifier()] = instance

        for identifier in save['deleted_identifiers']:
            self._deleted_identifiers.append(
                InstanceIdentifier.model_validate(identifier))

    def __hash__(self):
        values = (hash(value) for value in self._registry.values())

        return hash((frozenset(values),
                     frozenset(self._deleted_identifiers)))


class SemanticsManager(BaseModel):
    """
    The Semantic Manager is a static object that is delivered with
    each vocabulary model export.

    It provides the interface to interact with the local state and Fiware
    """

    instance_registry: InstanceRegistry = Field(
        description="Registry managing the local state"
    )
    class_catalogue: Dict[str, Type[SemanticClass]] = Field(
        default={},
        description="Register of class names to classes"
    )
    datatype_catalogue: Dict[str, Dict[str, str]] = Field(
        default={},
        description="Register of datatype names to Dict representation of "
                    "datatypes"
    )
    individual_catalogue: Dict[str, type] = Field(
        default={},
        description="Register of individual names to their classes"
    )

    default_header: InstanceHeader = Field(
        default=InstanceHeader(),
        description="Default header that each new instance receives if it "
                    "does not specify an own header"
    )

    @staticmethod
    def get_client(instance_header: InstanceHeader) \
            -> ContextBrokerClient:
        """Get the correct ContextBrokerClient to be used with the given header

        Args:
            instance_header (InstanceHeader): Header to be used with client
        Returns:
            ContextBrokerClient
        """
        if instance_header.ngsi_version == NgsiVersion.v2:
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
        if instance_header.ngsi_version == NgsiVersion.v2:
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
                                                 header=header,
                                                 enforce_new=True)
        else:
            loaded_class: SemanticDeviceClass = class_(id=entity.id,
                                                       header=header,
                                                       enforce_new=True)

        loaded_class.old_state.state = entity

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
                    field._set.add(converted_value)
                else:
                    field.add(converted_value)

        # load references into instance
        references_attribute = entity.get_attribute("referencedBy")
        references = references_attribute.value

        for identifier_str, prop_list in references.items():
            for prop in prop_list:
                loaded_class.add_reference(
                    InstanceIdentifier.model_validate_json(identifier_str.replace(
                        "---", ".")), prop)

        # load metadata
        metadata_dict = entity.get_attribute("metadata").value
        loaded_class.metadata.name = metadata_dict['name']
        loaded_class.metadata.comment = metadata_dict['comment']

        # load device_settings into instance, if instance is a device
        if isinstance(loaded_class, SemanticDeviceClass):
            settings_attribute = entity.get_attribute("deviceSettings")
            device_settings = DeviceSettings.model_validate(settings_attribute.value)

            for key, value in device_settings.model_dump().items():
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
                # we need to replace back --- with . that we switched,
                # as a . is not allowed in the dic in Fiware
                return InstanceIdentifier.model_validate_json(
                    str(value).replace("---", ".").replace("'", '"'))

        elif isinstance(field, CommandField):
            if isinstance(value, Command):
                return value
            # if loading local state, the wrong string delimters are used,
            # and the string is not automatically converted to a dict
            if not isinstance(value, dict):
                value = json.loads(value.replace("'", '"'))

            return Command(name=value['name'])
        elif isinstance(field, DeviceAttributeField):

            # if loading local state, the wrong string delimters are used,
            # and the string is not automatically converted to a dict

            if isinstance(value, DeviceAttribute):
                return value
            if not isinstance(value, dict):
                value = json.loads(value.replace("'", '"'))

            return DeviceAttribute(
                name=value['name'],
                attribute_type=value[
                    "attribute_type"]
            )

    def get_class_by_name(self, class_name: str) -> Type[SemanticClass]:
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

    def is_local_state_valid(self, validate_rules: bool = True) -> (bool, str):
        """
        Check if the local state is valid and can be saved.

        Args:
            validate_rules (bool): If true Rulefields are validated

        Returns:
            (bool, str): (Is valid?, Message)
        """

        if validate_rules:
            for instance in self.instance_registry.get_all():
                if isinstance(instance, Individual):
                    continue
                if not instance.are_rule_fields_valid():
                    return (
                        False,
                        f"SemanticEntity {instance.id} of type"
                        f"{instance.get_type()} has unfulfilled fields " 
                        f"{[f.name for f in instance.get_invalid_rule_fields()]}."
                    )

        for instance in self.instance_registry.get_all():
            if isinstance(instance, SemanticDeviceClass):
                if instance.device_settings.transport is None:
                    return (
                        False,
                        f"Device {instance.id} of type {instance.get_type()} " 
                        f"needs to be given an transport setting."
                    )
        return True, "State is valid"

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
        (valid, msg) = self.is_local_state_valid(validate_rules=assert_validity)

        if not valid:
            raise AssertionError(f"{msg}. Local state was not saved")

        # delete all instance that were loaded from Fiware and then deleted
        # wrap in try, as the entity could have been deleted by a third party
        for identifier in self.instance_registry.get_all_deleted_identifiers():

            # we need to handle devices and normal classes with different
            # clients

            client = self.get_client(instance_header=identifier.header)
            iota_client = self.get_iota_client(
                instance_header=identifier.header)
            try:
                client.delete_entity(
                    entity_id=identifier.id,
                    entity_type=identifier.type,
                    delete_devices=True,
                    iota_client=iota_client)
            except requests.RequestException:
                raise

            client.close()

        # merge with live state
        for instance in self.instance_registry.get_all():
            self.merge_local_and_live_instance_state(instance)

        # save, patch all local instances
        for instance in self.instance_registry.get_all():
            cb_client = self.get_client(instance_header=instance.header)
            if not isinstance(instance, SemanticDeviceClass):
                # it is important that we patch the values else the
                # references field would reach an invalid state if we worked
                # in parallel on an instance
                cb_client.patch_entity(instance.build_context_entity(),
                                       instance.old_state.state)
            else:
                iota_client = self.get_iota_client(
                    instance_header=instance.header)
                iota_client.patch_device(
                    device=instance.build_context_device(),
                    patch_entity=True,
                    cb_client=cb_client)
                iota_client.close()
            cb_client.close()
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
            return client.does_entity_exist(entity_id=identifier.id,
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

    def get_all_local_instances_of_class(self,
                                         class_: Optional[type] = None,
                                         class_name: Optional[str] = None,
                                         get_subclasses: bool = True) \
            -> List[SemanticClass]:
        """
        Retrieve all instances of a SemanitcClass from Local Storage

        Args:
            class_ (type):
                Type of classes to retrieve
            class_name (str):
                Name of type of classes to retrieve as string
            get_subclasses (bool):
                If true also all instances of subclasses
                of given class are returned

        Raises:
            AssertionError: If class_ and class_name are both None or non None

        Returns:
            List[SemanticClass]
        """

        assert class_ is None or class_name is None, \
            "Only one parameter is allowed"
        assert class_ is not None or class_name is not None, \
            "One parameter is required"

        if class_ is not None:
            class_name = class_.__name__
        else:
            class_ = self.get_class_by_name(class_name)

        res = []
        for instance in self.instance_registry.get_all():
            if not get_subclasses:
                if instance.get_type() == class_name:
                    res.append(instance)
            else:
                if isinstance(instance, class_):
                    res.append(instance)
        return res

    def load_instances_from_fiware(
            self,
            fiware_header: FiwareHeader,
            fiware_version: NgsiVersion,
            cb_url: str,
            iota_url: str,
            entity_ids: Optional[List[str]] = None,
            entity_types: Optional[List[str]] = None,
            id_pattern: str = None,
            type_pattern: str = None,
            q: Union[str, QueryString] = None,
            limit: int = inf,
    ) -> List[SemanticClass]:
        """
        Loads the instances of given types or ids from Fiware into the local
        state and returns the loaded instances

        Args:
            fiware_header (FiwareHeader): Fiware location to load
            fiware_version (NgsiVersion): Used fiware version
            cb_url (str): URL of the ContextBroker
            iota_url (str): URL of the IotaBroker
            entity_ids (Optional[str]): List of the entities ids that
                should be loaded
            entity_types (Optional[str]): List of the entities types that
                should be loaded
            id_pattern: A correctly formatted regular expression. Retrieve
                entities whose ID matches the regular expression. Incompatible
                with id, e.g. ngsi-ld.* or sensor.*
            type_pattern: A correctly formatted regular expression. Retrieve
                entities whose type matches the regular expression.
                Incompatible with type, e.g. room.*
            q (SimpleQuery): A query expression, composed of a list of
                statements separated by ;, i.e.,
                q=statement1;statement2;statement3. See Simple Query
                Language specification. Example: temperature>40.
            limit: Limits the number of entities to be retrieved Example: 20

        Raises:
           ValueError: if both entity_types and entity_ids are given
           ValueError: if Retrival of Context-entities fails
        Returns:
             List[SemanticClass]
        """

        header: InstanceHeader = InstanceHeader(
            service=fiware_header.service,
            service_path=fiware_header.service_path,
            cb_url=cb_url,
            iota_url=iota_url,
            ngsi_version=fiware_version
        )

        client = self.get_client(header)

        entities = client.get_entity_list(entity_ids=entity_ids,
                                          entity_types=entity_types,
                                          id_pattern=id_pattern,
                                          type_pattern=type_pattern,
                                          q=q,
                                          limit=limit)
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
        return Datatype.model_validate(self.datatype_catalogue[datatype_name])

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

    def visualize_local_state(
            self,
            display_individuals_rule: str = "ALL"
            ):
        """
        Visualise all instances in the local state in a network graph that
        shows which instances reference each other over which fields

        On execution of the methode a temporary image file is created and
        automatically displayed in the standard image viewing software of the
        system

        Args:
            display_individuals_rule (rule):
                If:
                "USED": Show only Individuals
                "ALL": Display all known Individuals
                "NONE": Display no Individuals
                that are connected to at least one instance
                else: Show all individuals

        Raises:
            ValueError: if display_individuals_rule is invalid
        """

        if not display_individuals_rule == "ALL" and \
            not display_individuals_rule == "NONE" and \
            not display_individuals_rule == "USED":

            raise ValueError(f"Invalid parameter {display_individuals_rule}")

        import igraph
        g = igraph.Graph(directed=True)

        for instance in self.get_all_local_instances():
            g.add_vertex(name=instance.id,
                         label=f"\n\n\n {instance.get_type()} \n {instance.id}",
                         color="green")

        used_individuals_names: Set[str] = set()
        for instance in self.get_all_local_instances():
            for field in instance.get_relation_fields():
                for linked in field.get_all():
                    if isinstance(linked, SemanticClass):
                        g.add_edge(instance.id, linked.id, name=field.name)
                        # g.es[-1]["name"] = field.name

                    elif isinstance(linked, SemanticIndividual):
                        if not display_individuals_rule == "NONE":
                            g.add_edge(instance.id, linked.get_name())
                            used_individuals_names.add(linked.get_name())

        if display_individuals_rule == "ALL":
            used_individuals_names.update(self.individual_catalogue.keys())
        for individual in [self.get_individual(name) for name in
                           used_individuals_names]:
            g.add_vertex(label=f"\n\n\n{individual.get_name()}",
                         name=individual.get_name(),
                         color="blue")

        layout = g.layout("fr")
        visual_style = {"vertex_size": 20,
                        "vertex_color": g.vs["color"],
                        "vertex_label": g.vs["label"],
                        "edge_label": g.es["name"],
                        "layout": layout,
                        "bbox": (len(g.vs) * 50, len(g.vs) * 50)}

        igraph.plot(g, **visual_style)

    def generate_cytoscape_for_local_state(
            self,
            display_only_used_individuals: bool = True
            ):
        """
        Generate a graph definition that can be loaded into a cytoscape
        visualisation tool, that describes the complete current local state.

        For the graph layout COLA is recommended with an edge length of 150

        Args:
            display_only_used_individuals (bool):
                If true(default): Show only Individuals that are connected to
                at least one instance
                else: Show all individuals

        Returns:
            Tupel of elements and stylesheet:
                elements is a dict:
                {"nodes": NODE_DEFINITIONS, "edges": EDGE_DEFINITIONS}
                stylesheet is a list containing all the graph styles
        """

        # graph design
        stylesheet = [
            {
                'selector': 'node',
                'style': {
                    'label': 'data(label)',
                    'z-index': 9999
                }
            },
            {
                'selector': 'edge',
                'style': {
                    'curve-style': 'bezier',
                    'target-arrow-color': 'black',
                    'target-arrow-shape': 'triangle',
                    'line-color': 'black',
                    "opacity": 0.45,
                    'z-index': 5000,
                }
            },
            {
                'selector': '.center',
                'style': {
                    'shape': 'rectangle',
                    'background-color': 'black'
                }
            },
            {
                'selector': '.individual',
                'style': {
                    'shape': 'circle',
                    'background-color': 'orange'
                }
            },
            {
                'selector': '.instance',
                'style': {
                    'shape': 'circle',
                    'background-color': 'green'
                }
            },
            {
                'selector': '.collection',
                'style': {
                    'shape': 'triangle',
                    'background-color': 'gray'
                }
            }
        ]

        nodes = []
        edges = []

        used_individual_names = set()
        if not display_only_used_individuals:
            used_individual_names.update(self.individual_catalogue.keys())

        def get_node_id(item: Union[SemanticClass, SemanticIndividual]) -> str:
            """
            Get the id to be used in the graph for an item

            Args:
                item (Union[SemanticClass, SemanticIndividual]): Item to get
                                                                    ID for

            Returns:
                str - ID
            """
            if isinstance(item, SemanticIndividual):
                return item.get_name()
            else:
                return item.get_identifier().model_dump_json()

        for instance in self.get_all_local_instances():
            label = f'({instance.get_type()}){instance.metadata.name}'
            nodes.append({'data': {'id': get_node_id(instance),
                                   'label': label,
                                   'parent_id': '',
                                   'classes': "instance item"},
                          'classes': "instance item"})

        for instance in self.get_all_local_instances():

            for rel_field in instance.get_relation_fields():

                values = rel_field.get_all()
                for v in values:
                    if isinstance(v, SemanticIndividual):
                        used_individual_names.add(v.get_name())

                if len(values) == 0:
                    pass
                elif len(values) == 1:
                    edge_id = uuid.uuid4().hex
                    edges.append({'data': {'id': edge_id,
                                           'source': get_node_id(instance),
                                           'target': get_node_id(values[0])}})
                    edge_name = rel_field.name
                    stylesheet.append({'selector': '#' + edge_id,
                                       'style': {'label': edge_name}})
                else:
                    edge_id = uuid.uuid4().hex
                    node_id = uuid.uuid4().hex
                    nodes.append({'data': {'id': node_id,
                                           'label': '',
                                           'parent_id': '',
                                           'classes': "collection"},
                                  'classes': "collection"})

                    edges.append({'data': {'id': edge_id,
                                           'source': get_node_id(instance),
                                           'target': node_id}})
                    edge_name = rel_field.name
                    stylesheet.append({'selector': '#' + edge_id,
                                       'style': {'label': edge_name}})

                    for value in values:
                        edge_id = uuid.uuid4().hex
                        edges.append({'data': {'id': edge_id,
                                               'source': node_id,
                                               'target': get_node_id(value)}})

        for individual_name in used_individual_names:
            nodes.append({'data': {'id': individual_name,
                                   'label': individual_name, 'parent_id': '',
                                   'classes': "individual item"},
                          'classes': "individual item"})

        elements = {'nodes': nodes, 'edges': edges}

        return elements, stylesheet

    def merge_local_and_live_instance_state(self, instance: SemanticClass) ->\
            None:
        """
        The live state of the instance is fetched from Fiware (if it exists)
        and the two states are merged:

        For each Field:
        - each added value (compared to old_state) is added to
        the live state
        - each deleted value (compared to old_state) is removed from
        the live state

        For each Device Settings (if instance is device):
        - If the device setting changed (compared to old_state) the live
        setting is overwritten

        For each Reference:
        - each added value (compared to old_state) is added to
        the live state
        - each deleted value (compared to old_state) is removed from
        the live state

        The new state is directly saved in the instance

        Args:
              instance (SemanticClass): instanced to be treated
        """

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
        if not client.does_entity_exist(entity_id=instance.id,
                                        entity_type=instance.get_type()):
            return

        client = self.get_client(instance.header)
        live_entity = client.get_entity(entity_id=instance.id,
                                        entity_type=instance.get_type())
        client.close()

        current_entity = instance.build_context_entity()
        old_entity = instance.old_state.state

        # ------merge fields-----------------------------------------------
        # instance exists already, add all locally added and delete all
        # locally deleted values to the/from the live_state

        for field in instance.get_fields():
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
            field._set.clear()  # very important to not use field.clear,
                                 # as that methode would also delete references
            for value in new_values:
                converted_value = self._convert_value_fitting_for_field(
                    field, value)
                field._set.add(converted_value)

        # ------merge references-----------------------------------------------
        merged_references: Dict = live_entity.get_attribute(
            "referencedBy").value
        current_references: Dict = current_entity.get_attribute(
            "referencedBy").value
        old_references: Dict = old_entity.get_attribute(
            "referencedBy").value

        keys = set(current_references.keys())
        keys.update(old_references.keys())

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
            # replace back the protected . (. not allowed in keys in fiware)
            instance.references[InstanceIdentifier.model_validate_json(key.replace(
                "---", "."))] = value

        # ------merge device settings----------------------------------------
        if isinstance(instance, SemanticDeviceClass):
            old_settings = old_entity.get_attribute("deviceSettings").value
            current_settings = \
                current_entity.get_attribute("deviceSettings").value
            new_settings = live_entity.get_attribute("deviceSettings").value

            # keys are always the same
            # override live state with local changes
            for key in old_settings:
                if old_settings[key] is not current_settings[key]:
                    new_settings[key] = current_settings[key]
                instance.device_settings.__setattr__(key, new_settings[key])

    def find_fitting_model(self, search_term: str, limit: int = 5) -> List[str]:
        """
        Find a fitting model by entering a search_term (e.g.: Sensor).
        The methode returns a selection from up-to [limit] possibly fitting
        model names. If a model name was selected from the proposition the
        model can be retrieved with the methode:
        "get_class_by_name(selectedName)"

        Args:
            search_term (str): search term to find a model by name
            limit (int): Max Number of suggested results (default: 5)

        Returns:
            List[str], containing 0 to [limit] ordered propositions (best first)
        """
        class_names = list(self.class_catalogue.keys())
        suggestions = [item[0] for item in process.extract(
            query=search_term.casefold(),
            choices=class_names,
            score_cutoff=50,
            limit=limit)]

        return suggestions
