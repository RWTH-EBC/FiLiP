import collections
import copy
import uuid
from enum import Enum
from typing import List, Any, Tuple, Dict, Type, TypeVar, Generic, \
    TYPE_CHECKING, Optional

from filip.models.base import DataType

from filip.models.ngsi_v2.context import ContextEntity, NamedContextAttribute

from filip.clients.ngsi_v2 import ContextBrokerClient

from filip.models import FiwareHeader
from pydantic import BaseModel, validator
from pydantic import Field as pyField

if TYPE_CHECKING:
    from filip.semantics.semantic_manager import SemanticManager

T = TypeVar('T')


class ClientSetting(str, Enum):
    unset = "unset"
    v2 = "v2"
    LD = "LD"


class InstanceIdentifier(BaseModel):
    id: str
    type: str
    fiware_header: FiwareHeader

    # def __eq__(self, other):
    #     return self.__class__ == other.__class__ and self.id == other.id and \
    #            self.type == other.type and self.fiware_header == f

    def __hash__(self):
        return hash(f'{self.type}-{self.id}-{self.fiware_header.service}-'
                    f'{self.fiware_header.service_path}')


class InstanceRegistry(BaseModel):
    _registry: Dict[InstanceIdentifier, 'SemanticClass'] = {}

    def register(self, instance: 'SemanticClass') -> bool:
        identifier = instance.get_identifier()

        if identifier in self._registry:
            return False
        else:
            self._registry[identifier] = instance
            return True

    def get(self, identifier: InstanceIdentifier):
        return self._registry[identifier]

    def contains(self, identifier: InstanceIdentifier):
        return identifier in self._registry


class Field(collections.MutableSequence):
    rule: str
    name: str
    instance_registry: InstanceRegistry

    def __init__(self, rule, name, semantic_manager):
        super().__init__()

        self.rule = rule
        self.name = name
        self.instance_registry = semantic_manager.instance_registry

        self.list = list()

    def is_valid(self) -> bool:
        pass

    def __len__(self): return len(self.list)

    def __getitem__(self, i): return self.list[i]

    def __delitem__(self, i): del self.list[i]

    def __setitem__(self, i, v):
        self.list[i] = v

    def insert(self, i, v):
        self.list.insert(i, v)

    def __str__(self):
        return str(self.list)

    def get_all(self):
        return self.list


class Relationship(Field):
    rule: str
    _rules: List[Tuple[str, List[List[Type]]]] = []
    _class_identifier: InstanceIdentifier

    # _model_catalogue: Dict[str, type]

    def is_valid(self) -> bool:
        """
        Check if the values present in this relationship fulfill the semantic
        rule.

        returns:
            bool
        """

        # rule has form: (STATEMENT, [[a,b],[c],[a,..],..])
        # A value fulfills the rule if it is an instance of all the classes
        #       listed in at least one innerlist
        # A field is fulfilled if a number of values fulfill the rule,
        #       the number is depending on the statement

        # The STATEMENTs and their according numbers are (STATEMENT|min|max):
        #       - only | len(values) | len(values)
        #       - some | 1 | len(values)
        #       - min n | n | len(values)
        #       - max n | 0 | n
        #       - range n,m | n | m

        # the relationship itself is a list
        values = self

        # loop over all rules, if a rule is not fulfilled return False
        for rule in self._rules:
            # rule has form: (STATEMENT, [[a,b],[c],[a,..],..])
            statement: str = rule[0]
            outer_class_list: List[List] = rule[1]

            # count how  many values fulfill this rule
            fulfilling_values = 0
            for v in values:

                # A value fulfills the rule if there exists an innerlist of
                # which the value is an instance of each value
                fulfilled = False
                for inner_class_list in outer_class_list:

                    counter = 0
                    for c in inner_class_list:
                        if isinstance(v, c):
                            counter += 1

                    if len(inner_class_list) == counter:
                        fulfilled = True

                if fulfilled:
                    fulfilling_values += 1

            # test if rule failed by evaluating the statement and the
            # number of fulfilling values
            if "min" in statement:
                number = int(statement.split("|")[1])
                if not fulfilling_values >= number:
                    return False
            elif "max" in statement:
                number = int(statement.split("|")[1])
                if not fulfilling_values <= number:
                    return False
            elif "exactly" in statement:
                number = int(statement.split("|")[1])
                if not fulfilling_values == number:
                    return False
            elif "some" in statement:
                if not fulfilling_values >= 1:
                    return False
            elif "only" in statement:
                if not fulfilling_values == len(values):
                    return False
            elif "value" in statement:
                if not fulfilling_values >= 1:
                    return False

        # no rule failed -> relationship fulfilled
        return True

    def __init__(self, rule, name, semantic_manager):
        super().__init__(rule, name, semantic_manager)

    def build_context_attribute(self) -> NamedContextAttribute:
        return NamedContextAttribute(
            name=self.name,
            type=DataType.RELATIONSHIP,
            value=[v.id for v in self]
        )

    def _check(self, v):
        assert isinstance(v, SemanticClass)

    def __getitem__(self, i) -> 'SemanticClass':
        return self.instance_registry.get(self.list[i])

    def __setitem__(self, i, v: 'SemanticClass'):
        self._check(v)
        self.list[i] = v.get_identifier()
        v.add_reference(self._class_identifier, self.name)

    def __delitem__(self, i):
        v: SemanticClass = self.instance_registry.get(self.list[i])
        v.remove_reference(self._class_identifier, self.name)
        del self.list[i]

    def insert(self, i, v: 'SemanticClass'):
        self._check(v)
        identifier = v.get_identifier()
        self.list.insert(i, identifier)
        v.add_reference(self._class_identifier, self.name)


def id_generator():
    return uuid.uuid4().hex


class SemanticClass(BaseModel):

    fiware_header: FiwareHeader
    id: str
    old_state: Optional[ContextEntity]

    _references: Dict[InstanceIdentifier, List[str]] = {}

    def add_reference(self, identifier: InstanceIdentifier, relation_name: str):
        if not identifier in self._references:
            self._references[identifier] = []
        self._references[identifier].append(relation_name)

    def remove_reference(self, identifier: InstanceIdentifier,
                         relation_name: str):
        self._references[identifier].remove(relation_name)
        if len(self._references[identifier]) == 0:
            del self._references[identifier]

    def __new__(cls, *args, **kwargs):
        semantic_manager = kwargs['semantic_manager']

        if 'id' in kwargs:
            instance_id = kwargs['id']
            if not instance_id == "":

                if 'fiware_header' in kwargs:
                    fiware_header = kwargs['fiware_header']
                else:
                    fiware_header = FiwareHeader()

                identifier = InstanceIdentifier(id=instance_id,
                                                type=cls.__name__,
                                                fiware_header=fiware_header)

                if semantic_manager.does_instance_exists(identifier=identifier):
                    return semantic_manager.load_instance(identifier=identifier)

        return super().__new__(cls)

    def __init__(self,  *args, **kwargs):
        semantic_manager = kwargs['semantic_manager']

        instance_id_ = kwargs['id'] if 'id' in kwargs else str(uuid.uuid4())
        fiware_header_ = kwargs['fiware_header'] \
            if 'fiware_header' in kwargs else FiwareHeader()
        old_state_ = kwargs['old_state'] if 'old_state' in kwargs else None

        identifier_ = InstanceIdentifier(
                        id= instance_id_,
                        type= self.get_type(),
                        fiware_header= fiware_header_
                    )
        # test if this instance was taken out of the instance_registry instead
        # of being newly created. If yes abort __init__(), to prevent state
        # overwrite !
        if semantic_manager.does_instance_exists(identifier_):
            return

        super().__init__(id=instance_id_, fiware_header=fiware_header_,
                         old_state=old_state_)
        assert not semantic_manager.client_setting == ClientSetting.unset

        semantic_manager.instance_registry.register(self)


    def are_fields_valid(self) -> bool:
        return len(self.get_invalid_fields()) == 0

    def get_invalid_fields(self) -> List[Field]:
        return [f for f in self.get_fields() if not f.is_valid()]

    def get_type(self) -> str:
        return self._get_class_name()

    def _get_class_name(self) -> str:
        return type(self).__name__

    def save(self, fiware_header: FiwareHeader, assert_validity: bool = False):

        if assert_validity:
            assert self.are_fields_valid(), \
                f"Attempted to save the SemanticEntity {self.id} of type " \
                f"{self._get_class_name()} with invalid fields " \
                f"{[f.name for f in self.get_invalid_fields()]}"

        with ContextBrokerClient(fiware_header=fiware_header) as client:
            client.patch_entity(entity=self.build_context_entity(),
                                old_entity=self._old_state)

    def delete(self, assert_no_references: bool = False):
        pass

    def get_fields(self) -> List[Field]:
        fields: List[Field] = self.get_relationships()
        # todo datafields
        return fields

    def get_field_names(self) -> List[str]:
        names = self.get_relationship_names()
        # todo datafields
        return names

    def get_relationships(self) -> List[Relationship]:
        relationships = []
        for key, value in self.__dict__.items():
            if isinstance(value, Relationship):
                rel: Relationship = value
                relationships.append(rel)
        return relationships

    def get_relationship_names(self) -> List[str]:
        names = []
        for key, value in self.__dict__.items():
            if isinstance(value, Relationship):
                names.append(key)
        return names

    def get_field_by_name(self, field_name: str) -> Field:
        for key, value in self.__dict__.items():
            if isinstance(value, Field):
                if value.name == field_name:
                    return value

        raise KeyError

    def build_context_entity(self) -> ContextEntity:

        entity = ContextEntity(
            id=self.id,
            type=self._get_class_name()
        )

        for rel in self.get_relationships():
            entity.add_attributes([rel.build_context_attribute()])

        # todo datafields
        return entity

    def get_identifier(self) -> InstanceIdentifier:
        return InstanceIdentifier(id=self.id, type=self.get_type(),
                                  fiware_header=self.fiware_header)

    class Config:
        arbitrary_types_allowed = True
        allow_mutation = False


class SemanticIndividual(SemanticClass):

    @staticmethod
    def _validate(values: List[Any], rules: Tuple[str, List[List]]):
        assert False, "Object is an instance, Instances are valueless"


class ModelCatalogue(BaseModel):
    catalogue: Dict[str, type]


