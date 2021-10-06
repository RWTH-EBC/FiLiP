import collections
import copy
import json
import uuid
from enum import Enum
from typing import List, Any, Tuple, Dict, Type, TypeVar, Generic, \
    TYPE_CHECKING, Optional, Union


from filip.models.base import DataType

from filip.models.ngsi_v2.context import ContextEntity, NamedContextAttribute


from filip.models import FiwareHeader
from pydantic import BaseModel, validator, Field, AnyHttpUrl
from filip.config import settings

if TYPE_CHECKING:
    from filip.semantics.semantic_manager import SemanticManager


class FiwareVersion(str, Enum):
    v2 = "v2"
    LD = "LD"


class InstanceHeader(FiwareHeader):

    url: str = Field(default=settings.CB_URL)
    fiware_version: FiwareVersion = Field(default=FiwareVersion.v2)

    def get_fiware_header(self) -> FiwareHeader:
        return FiwareHeader(service=self.service,
                            service_path=self.service_path)
    class Config:
        frozen = True


class InstanceIdentifier(BaseModel):
    id: str
    type: str
    header: InstanceHeader

    # def __eq__(self, other):
    #     return self.__class__ == other.__class__ and self.id == other.id and \
    #            self.type == other.type and self.header == f

    # def __hash__(self):
    #     return hash(f'{self.type}-{self.id}-{self.header.service}-'
    #                 f'{self.header.service_path}')
    #
    # def __str__(self):
    #     return hash(f'{self.type}|{self.id}|{self.header.service}|'
    #                 f'{self.header.service_path}')

    class Config:
        frozen = True


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

    def get_all(self) -> List['SemanticClass']:
        return list(self._registry.values())


class Datatype(BaseModel):
    type: str
    """Type of the datatype"""
    number_has_range: bool
    """If Type==Number: Does the datatype define a range"""
    number_range_min: Union[int, str]
    """If Type==Number: Min value of the datatype range, 
        if a range is defined"""
    number_range_max: Union[int, str]
    """If Type==Number: Max value of the datatype range, 
        if a range is defined"""
    number_decimal_allowed: bool
    """If Type==Number: Are decimal numbers allowed?"""
    forbidden_chars: List[str]
    """If Type==String: Blacklisted chars"""
    allowed_chars: List[str]
    """If Type==String: Whitelisted chars"""
    enum_values: List[str]
    """If Type==Enum: Enum values"""

    def value_is_valid(self, value: str) -> bool:
        """Test if value is valid for this datatype.
        Numbers are also given as strings

        Args:
            value (str): value to be tested

        Returns:
            bool
        """

        if self.type == "string":
            if len(self.allowed_chars) > 0:
                # if allowed chars is empty all chars are allowed
                for char in value:
                    if char not in self.allowed_chars:
                        return False
            for char in self.forbidden_chars:
                if char in value:
                    return False
            return True

        if self.type == "number":

            if self.number_decimal_allowed:
                try:
                    number = float(value)
                except:
                    return False
            else:
                try:
                    number = int(value)
                except:
                    return False

            if not self.number_range_min == "/":
                if number < self.number_range_min:
                    return False
            if not self.number_range_max == "/":
                if number > self.number_range_max:
                    return False

            return True

        if self.type == "enum":
            return value in self.enum_values

        if self.type == "date":
            try:
                from dateutil.parser import parse
                parse(value, fuzzy=False)
                return True

            except ValueError:
                return False

        return True


class Field(collections.MutableSequence):
    _rules: List[Tuple[str, List[List[str]]]]
    rule: str
    name: str
    _semantic_manager: 'SemanticManager'

    def __init__(self, rule, name, semantic_manager):
        self._semantic_manager = semantic_manager
        super().__init__()

        self.rule = rule
        self.name = name

        self.list = list()

    def is_valid(self) -> bool:
        """
                Check if the values present in this relationship fulfill the semantic
                rule.

                returns:
                    bool
                """

        # rule has form: (STATEMENT, [[a,b],[c],[a,..],..])
        # A value fulfills the rule if it is an instance of all the classes,
        #       datatype_catalogue listed in at least one innerlist
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
            outer_list: List[List] = rule[1]

            # count how  many values fulfill this rule
            fulfilling_values = 0
            for v in values:

                # A value fulfills the rule if there exists an innerlist of
                # which the value is an instance of each value
                fulfilled = False
                for inner_list in outer_list:

                    counter = 0
                    for rule_value in inner_list:
                        if self._value_is_valid(v, rule_value):
                            counter += 1

                    if len(inner_list) == counter:
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

    def _value_is_valid(self, value, rule_value) -> bool:
        pass

    def build_context_attribute(self) -> NamedContextAttribute:
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


class DataField(Field):
    _rules: List[Tuple[str, List[List[str]]]] = []

    def _value_is_valid(self, value, rule_value: str) -> bool:
        datatype = self._semantic_manager.get_datatype(rule_value)
        return datatype.value_is_valid(value)

    def build_context_attribute(self) -> NamedContextAttribute:
        return NamedContextAttribute(
            name=self.name,
            type=DataType.STRUCTUREDVALUE,
            value=[v for v in self.get_all()]
        )


class RelationField(Field):
    _rules: List[Tuple[str, List[List[Type]]]] = []
    _class_identifier: InstanceIdentifier

    def _value_is_valid(self, value, rule_value: type) -> bool:
        if isinstance(value, SemanticClass):
            return isinstance(value, rule_value)
        elif isinstance(value, SemanticIndividual):
            return value.is_instance_of_class(rule_value)
        else:
            return False

    def build_context_attribute(self) -> NamedContextAttribute:

        values = []
        for v in self.get_all():
            if isinstance(v, InstanceIdentifier):
                values.append(v.dict())
            else:
                values.append(v)

        return NamedContextAttribute(
            name=self.name,
            type=DataType.RELATIONSHIP,
            value=values
        )

    def __getitem__(self, i) -> Union['SemanticClass', 'SemanticIndividual']:
        v = self.list[i]
        if isinstance(v, InstanceIdentifier):
            return self._semantic_manager.get_instance(v)
        else:
            return self._semantic_manager.get_individual(v)

    def __setitem__(self, i, v: Union['SemanticClass', 'SemanticIndividual']):
        if isinstance(v, SemanticClass):
            self.list[i] = v.get_identifier()
            v.add_reference(self._class_identifier, self.name)
        elif isinstance(v, SemanticIndividual):
            self.list[i] = v.get_name()
        else:
            raise AttributeError("Only instances of a SemanticClass or a "
                                 "SemanticIndividual can be given as value")

    def __delitem__(self, i):
        v = self.list[i]
        if isinstance(v, InstanceIdentifier):
            v: SemanticClass = self._semantic_manager.get_instance(self.list[i])
            v.remove_reference(self._class_identifier, self.name)
            del self.list[i]
        else:
            del self.list[i]

    def insert(self, i, v: Union['SemanticClass', 'SemanticIndividual']):

        if isinstance(v, SemanticClass):
            identifier = v.get_identifier()
            self.list.insert(i, identifier)
            v.add_reference(self._class_identifier, self.name)
        elif isinstance(v, SemanticIndividual):
            self.list.insert(i, v.get_name())
        else:
            raise AttributeError("Only instances of a SemanticClass or a "
                                 "SemanticIndividual can be given as value")




class SemanticClass(BaseModel):

    header: InstanceHeader
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

        if 'enforce_new' in kwargs:
            enforce_new = kwargs['enforce_new']
        else:
            enforce_new = False

        if 'identifier' in kwargs:
            instance_id = kwargs['identifier'].id
            header = kwargs['identifier'].header
            assert cls.__name__ == kwargs['identifier'].type
        else:
            instance_id = kwargs['id'] if 'id' in kwargs else ""
            header = kwargs['header'] \
                if 'header' in kwargs else InstanceHeader()

        if not instance_id == "" and not enforce_new:

            identifier = InstanceIdentifier(id=instance_id,
                                            type=cls.__name__,
                                            header=header)

            if semantic_manager.does_instance_exists(identifier=identifier):
                return semantic_manager.load_instance(identifier=identifier)

        return super().__new__(cls)

    def __init__(self,  *args, **kwargs):
        semantic_manager = kwargs['semantic_manager']

        if 'identifier' in kwargs:
            instance_id_ = kwargs['identifier'].id
            header_ = kwargs['identifier'].header
            assert self.get_type() == kwargs['identifier'].type
        else:
            instance_id_ = kwargs['id'] if 'id' in kwargs \
                                        else str(uuid.uuid4())
            header_ = kwargs['header'] if 'header' in kwargs \
                                        else InstanceHeader()

        old_state_ = kwargs['old_state'] if 'old_state' in kwargs else None

        identifier_ = InstanceIdentifier(
                        id=instance_id_,
                        type=self.get_type(),
                        header=header_
                    )

        if 'enforce_new' in kwargs:
            enforce_new = kwargs['enforce_new']
        else:
            enforce_new = False

        # test if this instance was taken out of the instance_registry instead
        # of being newly created. If yes abort __init__(), to prevent state
        # overwrite !
        if not enforce_new:
            if semantic_manager.does_instance_exists(identifier_):
                return

        super().__init__(id=instance_id_, header=header_,
                         old_state=old_state_)

        semantic_manager.instance_registry.register(self)

    def are_fields_valid(self) -> bool:
        return len(self.get_invalid_fields()) == 0

    def get_invalid_fields(self) -> List[Field]:
        return [f for f in self.get_fields() if not f.is_valid()]

    def get_type(self) -> str:
        return self._get_class_name()

    def _get_class_name(self) -> str:
        return type(self).__name__

    # def save(self, assert_validity: bool = False):
    #
    #     if assert_validity:
    #         assert self.are_fields_valid(), \
    #             f"Attempted to save the SemanticEntity {self.id} of type " \
    #             f"{self._get_class_name()} with invalid fields " \
    #             f"{[f.name for f in self.get_invalid_fields()]}"
    #
    #     with ContextBrokerClient(
    #             fiware_header=self.header.get_fiware_header()) as client:
    #         client.patch_entity(entity=self.build_context_entity(),
    #                             old_entity=self.old_state)

    def delete(self, assert_no_references: bool = False):
        # todo ?
        pass

    def get_fields(self) -> List[Field]:
        fields: List[Field] = self.get_relation_fields()
        fields.extend(self.get_data_fields())
        return fields

    def get_field_names(self) -> List[str]:
        return [f.name for f in self.get_fields()]

    def get_relation_fields(self) -> List[RelationField]:
        relationships = []
        for key, value in self.__dict__.items():
            if isinstance(value, RelationField):
                rel: RelationField = value
                relationships.append(rel)
        return relationships

    def get_data_fields(self) -> List[DataField]:
        fields = []
        for key, value in self.__dict__.items():
            if isinstance(value, DataField):
                fields.append(value)
        return fields

    def get_relation_field_names(self) -> List[str]:
        return [f.name for f in self.get_relation_fields()]

    def get_data_field_names(self) -> List[str]:
        return [f.name for f in self.get_data_fields()]

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

        for field in self.get_fields():
            entity.add_attributes([field.build_context_attribute()])

        return entity

    def get_identifier(self) -> InstanceIdentifier:
        return InstanceIdentifier(id=self.id, type=self.get_type(),
                                  header=self.header)

    class Config:
        arbitrary_types_allowed = True
        allow_mutation = False


class SemanticIndividual(BaseModel):
    _parent_classes: List[type]

    def __eq__(self, other):
        return type(self) == type(other)

    def __str__(self):
        return type(self).__name__

    def get_name(self):
        return type(self).__name__

    def is_instance_of_class(self, class_: type) -> False:

        if isinstance(self, class_):
            return True
        for parent in self._parent_classes:
            if isinstance(parent(), class_):
                return True
        return False



