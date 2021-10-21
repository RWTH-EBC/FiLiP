import collections
import copy
import json
import uuid
from enum import Enum
from typing import List, Any, Tuple, Dict, Type, TypeVar, Generic, \
    TYPE_CHECKING, Optional, Union

import requests
from dominate.tags import sup

from filip.models.ngsi_v2.iot import Device, ExpressionLanguage, \
    TransportProtocol
import filip.models.ngsi_v2.iot as iot
from filip.models.base import DataType, NgsiVersion

from filip.models.ngsi_v2.context import ContextEntity, NamedContextAttribute


from filip.models import FiwareHeader
from pydantic import BaseModel, validator, Field, AnyHttpUrl
from filip.config import settings
from filip.semantics.vocabulary_configurator import label_blacklist, \
    label_char_whitelist

if TYPE_CHECKING:
    from filip.semantics.semantic_manager import SemanticManager


class InstanceHeader(FiwareHeader):
    """
    Header of a SemanticClass instance, describes the Fiware Location were
    the instance will be / is saved.
    The header is not bound to one Fiware Setup, but can describe the
    exact location in the web
    """

    cb_url: str = Field(default=settings.CB_URL,
                        description="Url of the ContextBroker from the Fiware "
                                    "setup")
    iota_url: str = Field(default=settings.IOTA_URL,
                          description="Url of the IoTABroker from the Fiware "
                                      "setup")

    fiware_version: NgsiVersion = Field(default=NgsiVersion.v2,
                                        description="Used Version in the "
                                                      "Fiware setup")

    def get_fiware_header(self) -> FiwareHeader:
        """
        Get a Filip FiwareHeader from the InstanceHeader
        """
        return FiwareHeader(service=self.service,
                            service_path=self.service_path)

    class Config:
        """
        The location of the instance needs to be fixed, and is not changeable.
        Frozen is further needed so that the header can be used as a hash key
        """
        frozen = True


class InstanceIdentifier(BaseModel):
    """
    Each Instance of a SemanticClass posses a unique identifier that is
    directly linked to one Fiware entry
    """
    id: str = Field(description="Id of the entry in Fiware")
    type: str = Field(description="Type of the entry in Fiware, equal to "
                                  "class_name")
    header: InstanceHeader = Field(description="describes the Fiware "
                                               "Location were the instance "
                                               "will be / is saved.")

    class Config:
        """
        The identifier of the instance needs to be fixed, and is not changeable.
        Frozen is further needed so that the identifier can be used as a hash
        key
        """
        frozen = True


class Datatype(BaseModel):
    """
    Model of a vocabulary/ontology Datatype used to validate assignments in
    DataFields
    """
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


class DeviceProperty(BaseModel):
    name: str
    _instance_identifier: Optional[InstanceIdentifier] = None
    _semantic_manager: Optional['SemanticManager'] = None
    _field_name: Optional[str] = None

    def _get_instance(self) -> 'SemanticClass':
        return self._semantic_manager.get_instance(self._instance_identifier)

    # def __eq__(self, other):
    #     return type(other) == type(self) and self.name == other.name and \
    #            self._field_name == other._field_name

    def _get_field_from_fiware(self, field_name: str, required_type: str) \
            -> NamedContextAttribute:

        if self._field_name is None:
            raise Exception("This DeviceProperty needs to be added to a "
                            "device field of an SemanticDeviceClass instance "
                            "and the state saved before this methode can be "
                            "executed")

        try:
            entity = self._semantic_manager.get_entity_from_fiware(
                            instance_identifier=self._instance_identifier)
        except requests.RequestException:
            raise Exception("The instance to which this property belongs is "
                            "not yet present in Fiware, you need to save the "
                            "state first")
        try:
            attr = entity.get_attribute(field_name)
        except requests.RequestException:
            raise Exception("This property was not yet saved in Fiware. "
                            "You need to save the state first before this "
                            "methode can be executed")

        if not attr.type == required_type:
            raise Exception("The field in Fiware has a wrong type, "
                            "an uncaught naming conflict happened")

        if not attr.type == required_type:
            raise Exception("The field in Fiware has a wrong type, "
                            "an uncaught naming conflict happened")
        return attr

    def get_all_field_names(self) -> List[str]:
        pass

    class Config:
        underscore_attrs_are_private = True


class Command(DeviceProperty):

    def send(self):

        attr = self._get_field_from_fiware(field_name=self.name,
                                           required_type="command")
        client = self._semantic_manager.get_client(
                 self._instance_identifier.header)

        client.update_entity_attribute(entity_id=self._instance_identifier.id,
                                       attr=attr)
        client.close()


    def get_info(self) -> str:
        return self._get_field_from_fiware(field_name=f'{self.name}_info',
                                           required_type="commandResult").value

    def get_status(self):
        return self._get_field_from_fiware(field_name=f'{self.name}_status',
                                           required_type="commandStatus").value

    def get_all_field_names(self) -> List[str]:
        return [self.name, f"{self.name}_info", f"{self.name}_result"]


class DeviceAttributeType(str, Enum):
    lazy = "lazy"
    active = "active"


class DeviceAttribute(DeviceProperty):
    attribute_type: DeviceAttributeType

    def get_value(self):
        return self._get_field_from_fiware(
            field_name=f'{self._field_name}_{self.name}',
            required_type="StructuredValue").value

    # def get_full_field_name(self) -> str:
    #     return f'{self._field_name}_{self.name}'

    def get_all_field_names(self) -> List[str]:
        return [f'{self._field_name}_{self.name}']

    # def __eq__(self, other):
    #     return super.__eq__(self, other) and \
    #            self.attribute_type == other.attribute_type

    class Config:
        use_enum_values = True


class Field(collections.MutableSequence, BaseModel):
    """
    A Field corresponds to a CombinedRelation for a class from the vocabulary.
    It itself is a _list, that is enhanced with methods to provide validation
    of the values according to the rules stated in the vocabulary

    The fields of a class are predefined. A field can contain standard values
    on init
    """

    name: str = ""
    """Name of the Field, corresponds to the property name that it has in the 
    SemanticClass"""

    _semantic_manager: 'SemanticManager'
    """Reference to the global SemanticManager"""

    _instance_identifier: InstanceIdentifier
    """Identifier of instance, that has this field as property"""

    _list: List = list()

    def __init__(self,  name, semantic_manager):
        self._semantic_manager = semantic_manager
        super().__init__()
        self.name = name
        self._list = list()

    def is_valid(self) -> bool:
        pass

    def build_context_attribute(self) -> NamedContextAttribute:
        """
        Convert the field to a NamedContextAttribute that can eb added to a
        ContextEntity

        Returns:
            NamedContextAttribute
        """
        pass
    
    def build_device_attributes(self) -> List[Union[iot.DeviceAttribute,
                                                    iot.LazyDeviceAttribute,
                                                    iot.StaticDeviceAttribute,
                                                    iot.DeviceCommand]]:
        values = []
        for v in self.get_all():
            if isinstance(v, BaseModel):
                values.append(v.dict())
            else:
                values.append(v)

        x = [
            iot.StaticDeviceAttribute(
                name=self.name,
                type=DataType.STRUCTUREDVALUE,
                value=values,
                entity_name=None,
                entity_type=None,
                reverse=None,
                expression=None,
                metadata=None,
            )
        ]

        return x

    # List methods
    def __len__(self): return len(self._list)
    def __getitem__(self, i): return self._list[i]
    def __delitem__(self, i): del self._list[i]
    def __setitem__(self, i, v): self._list[i] = v
    def insert(self, i, v): self._list.insert(i, v)

    def set(self, values: List):
        """
        Set the values of the field equal to the given list

        Args:
            values: List of values fitting for the field

        Returns:
            None
        """
        self.clear()

        i = 0
        for v in values:
            self.insert(i, v)
            i += 1

    def __str__(self):
        """
        Get Field in a nice readable way

        Returns:
            str
        """
        result = f'Field: {self.name},\n\tvalues: ['
        values = self.get_all()
        for value in values:
            result += f'{value}, '
        if len(values) > 0:
            result = result[:-2]
        return result

    def get_all(self):
        """
        Get all values of the field
        """
        return self._list

    def _get_instance(self) -> 'SemanticClass':
        return self._semantic_manager.get_instance(self._instance_identifier)

    # def __eq__(self, other):
    #     if not type(self) == type(other):
    #         return False
    #     if not len(self._list) == len(other._list):
    #         return False
    #     for i in range(len(self._list)):
    #         if not self._list[i] == other._list[i]:
    #             return False
    #     return True

    def get_field_names(self) -> List[str]:
        return [self.name]

    class Config:
        underscore_attrs_are_private = True

    def values_to_json(self) -> List[str]:
        res = []
        for v in self.get_all():
            if isinstance(v, BaseModel):
                res.append(v.json())
            else:
                res.append(v)
        return res


class DeviceField(Field):

    _internal_type: type = DeviceProperty

    def is_valid(self) -> bool:
        for value in self.get_all():
            if not isinstance(value, self._internal_type):
                return False
        return True

    def _pre_set(self, v):
        assert isinstance(v, self._internal_type)
        assert v._instance_identifier is None, "DeviceProperty can only " \
                                               "belong to one device instance"
        v._instance_identifier = self._instance_identifier
        v._semantic_manager = self._semantic_manager
        v._field_name = self.name

    def _name_check(self, v: _internal_type):
        taken_fields = self._get_instance().get_all_field_names()
        for name in v.get_all_field_names():
            if name in taken_fields:
                raise NameError(f"The property can not be added to the field "
                                 f"{self.name}, because the instance already"
                                 f" posses a field with the name {name}")
            if name in label_blacklist:
                raise NameError(f"The property can not be added to the field "
                                f"{self.name}, because the name {name} is "
                                f"forbidden")

            for c in name:
                if c not in label_char_whitelist:
                    raise NameError(
                        f"The property can not be added to the field "
                        f"{self.name}, because the name {name} "
                        f"contains the forbidden character {c}")

    def __delitem__(self, i):
        v = self._list[i]
        v._instance_identifier = None
        v._semantic_manager = None
        v.name = None
        del self._list[i]
        
    def __setitem__(self, i, v): 
        self._pre_set(v)
        self._name_check(v)
        super(DeviceField, self).__setitem__(i, v)
        
    def insert(self, i, v):
        self._pre_set(v)
        self._name_check(v)
        super(DeviceField, self).insert(i, v)

    def get_field_names(self) -> List[str]:
        names = super().get_field_names()
        for v in self.get_all():
            names.extend(v.get_all_field_names())
        return names

    # needed when saving local state
    def build_context_attribute(self) -> NamedContextAttribute:
        values = []
        for v in self.get_all():
            if isinstance(v, BaseModel):
                values.append(v.dict())
            else:
                values.append(v)
        return NamedContextAttribute(name=self.name, value=values)

class CommandField(DeviceField):

    _internal_type = Command

    def get_all(self) -> List[Command]:
        return super().get_all()

    def __getitem__(self, i) -> Command:
        return super(CommandField, self).__getitem__(i)

    def build_device_attributes(self) -> List[Union[iot.DeviceAttribute,
                                                    iot.LazyDeviceAttribute,
                                                    iot.StaticDeviceAttribute,
                                                    iot.DeviceCommand]]:

        attrs = super().build_device_attributes()

        for command in self.get_all():
            attrs.append(
                iot.DeviceCommand(
                    name=command.name,
                )
            )

        return attrs


class DeviceAttributeField(DeviceField):
    _internal_type = DeviceAttribute

    def __getitem__(self, i) -> DeviceAttribute:
        return super().__getitem__(i)

    def get_all(self) -> List[DeviceAttribute]:
        return super().get_all()

    def build_device_attributes(self) -> List[Union[iot.DeviceAttribute,
                                                    iot.LazyDeviceAttribute,
                                                    iot.StaticDeviceAttribute,
                                                    iot.DeviceCommand]]:
        attrs = super().build_device_attributes()

        for attribute in self.get_all():

            if attribute.attribute_type == DeviceAttributeType.active:
                attrs.append(
                    iot.DeviceAttribute(
                        object_id=attribute.name,
                        name=f"{self.name}_{attribute.name}",
                        type=DataType.STRUCTUREDVALUE,
                        entity_name=None,
                        entity_type=None,
                        reverse=None,
                        expression=None,
                        metadata=None
                    )
                )
            else:
                attrs.append(
                    iot.LazyDeviceAttribute(
                        object_id=attribute.name,
                        name=f"{self.name}_{attribute.name}",
                        type=DataType.STRUCTUREDVALUE,
                        entity_name=None,
                        entity_type=None,
                        reverse=None,
                        expression=None,
                        metadata=None
                    )
                )

        return attrs


class RuleField(Field):
    """
    A RuleField corresponds to a CombinedRelation for a class from the
    vocabulary.
    It itself is a _list, that is enhanced with methods to provide validation
    of the values according to the rules stated in the vocabulary

    The fields of a class are predefined. A field can contain standard values
    on init
    """

    _rules: List[Tuple[str, List[List[str]]]]
    """rule formatted for machine readability """
    rule: str = ""
    """rule formatted for human readability """

    def __init__(self, rule, name, semantic_manager):
        self._semantic_manager = semantic_manager
        super().__init__(name, semantic_manager)
        self.rule = rule

    def is_valid(self) -> bool:
        """
        Check if the values present in this relationship fulfills the semantic
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

        # the relationship itself is a _list
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
        """
        Test if a value of the field, fulfills a part of a rule

        Args:
            value: Value in field
            rule_value: Value from inner List of rules_

        Returns:
            bool, True if valid
        """
        pass

    # List methods
    def __len__(self): return len(self._list)
    def __getitem__(self, i): return self._list[i]
    def __delitem__(self, i): del self._list[i]
    def __setitem__(self, i, v): self._list[i] = v
    def insert(self, i, v): self._list.insert(i, v)

    def __str__(self):
        """
        Get Field in a nice readable way

        Returns:
            str
        """
        result = super(RuleField, self).__str__()
        result += f'],\n\trule: ({self.rule})'
        return result

    def get_all(self):
        """
        Get all values of the field
        """
        return self._list


class DataField(RuleField):
    """
    Field for CombinedDataRelation
    A Field that contains literal values: str, int, ...
    """

    def _value_is_valid(self, value, rule_value: str) -> bool:
        datatype = self._semantic_manager.get_datatype(rule_value)
        return datatype.value_is_valid(value)

    def build_context_attribute(self) -> NamedContextAttribute:
        return NamedContextAttribute(
            name=self.name,
            type=DataType.STRUCTUREDVALUE,
            value=[v for v in self.get_all()]
        )

    def __str__(self):
        return 'Data'+super().__str__()


class RelationField(RuleField):
    """
       Field for CombinedObjectRelation
       A Field that contains links to other instances of SemanticClasses,
       or Individuals

       Internally this field only holds:
            - InstanceIdentifiers for SemanticClasses. If a value is accessed
                the corresponding instance is loaded form the local registry
                or hot loaded form Fiware
            - Names for Individuals. If a value is accessed a new object of
                that individual is returned (All instances are equal)
    """
    _rules: List[Tuple[str, List[List[Type]]]] = []

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
        v = self._list[i]
        if isinstance(v, InstanceIdentifier):
            return self._semantic_manager.get_instance(v)
        else:
            return self._semantic_manager.get_individual(v)

    def __setitem__(self, i, v: Union['SemanticClass', 'SemanticIndividual']):
        """ see class description
        Raises:
            AttributeError: if value not an instance of 'SemanticClass' or
            'SemanticIndividual'
        """
        if isinstance(v, SemanticClass):
            self._list[i] = v.get_identifier()
            v.add_reference(self._instance_identifier, self.name)
        elif isinstance(v, SemanticIndividual):
            self._list[i] = v.get_name()
        else:
            raise AttributeError("Only instances of a SemanticClass or a "
                                 "SemanticIndividual can be given as value")

    def __delitem__(self, i):
        """ see class description"""
        if isinstance(self._list[i], InstanceIdentifier):
            if not self._semantic_manager.was_instance_deleted(self._list[i]):
                v: SemanticClass = self._semantic_manager.get_instance(self._list[i])

                v.remove_reference(self._instance_identifier, self.name)
            del self._list[i]
        else:
            del self._list[i]

    def insert(self, i, v: Union['SemanticClass', 'SemanticIndividual']):
        """ see class description
        Raises:
            AttributeError: if value not an instance of 'SemanticClass' or
            'SemanticIndividual'
        """

        if isinstance(v, SemanticClass):
            identifier = v.get_identifier()
            self._list.insert(i, identifier)
            v.add_reference(self._instance_identifier, self.name)
        elif isinstance(v, SemanticIndividual):
            self._list.insert(i, v.get_name())
        else:
            raise AttributeError("Only instances of a SemanticClass or a "
                                 "SemanticIndividual can be given as value")

    def __str__(self):
        """ see class description"""
        return 'Relation'+super().__str__()


class InstanceState(BaseModel):
    state: Optional[ContextEntity]


class SemanticClass(BaseModel):
    """
    A class representing a vocabulary/ontology class.
    A class has predefined fields
    Each instance of a class links to a unique Fiware ContextEntity (by
    Identifier)

    If a class is initiated it is first looked if this instance (equal over
    identifier) exists in the local registry. If yes that instance is returned

    If no, it is looked if this instance exists in Fiware, if yes it is
    loaded and returned, else a new instance of the class is initialised and
    returned
    """

    header: InstanceHeader
    """Header of instance. Holds the information where the instance is saved 
    in Fiware"""
    id: str
    """Id of the instance, equal to Fiware ContextEntity Id"""
    old_state: InstanceState = InstanceState()
    """State in Fiware the moment the instance was loaded in the local 
    registry. Used when saving. Only the made changes are reflected"""

    references: Dict[InstanceIdentifier, List[str]] = {}
    """references made to this instance in other instances RelationFields"""

    semantic_manager: BaseModel = None

    def add_reference(self, identifier: InstanceIdentifier, relation_name: str):
        """
        Note that an instance references this instance in the relation

        Args:
            identifier (InstanceIdentifier): Identifier of the referencing
                                             instance
            relation_name (str): Field name in which the reference is taking
                                 place
        """
        if identifier not in self.references:
            self.references[identifier] = []
        self.references[identifier].append(relation_name)

    def remove_reference(self, identifier: InstanceIdentifier,
                         relation_name: str):
        """
        Remove the note of reference

        Args:
           identifier (InstanceIdentifier): Identifier of the referencing
                                            instance
           relation_name (str): Field name in which the reference is taking
                                place
        """
        self.references[identifier].remove(relation_name)
        if len(self.references[identifier]) == 0:
            del self.references[identifier]

    def __new__(cls, *args, **kwargs):
        semantic_manager_ = kwargs['semantic_manager']

        if 'enforce_new' in kwargs:
            enforce_new = kwargs['enforce_new']
        else:
            enforce_new = False

        if 'identifier' in kwargs:
            instance_id = kwargs['identifier'].id
            header_ = kwargs['identifier'].header
            assert cls.__name__ == kwargs['identifier'].type
        else:
            instance_id = kwargs['id'] if 'id' in kwargs else ""
            header_ = kwargs['header'] \
                if 'header' in kwargs else \
                semantic_manager_.get_default_header()

        if not instance_id == "" and not enforce_new:

            identifier = InstanceIdentifier(id=instance_id,
                                            type=cls.__name__,
                                            header=header_)

            if semantic_manager_.does_instance_exists(identifier=identifier):
                return semantic_manager_.load_instance(identifier=identifier)

        return super().__new__(cls)

    def __init__(self,  *args, **kwargs):
        semantic_manager_ = kwargs['semantic_manager']

        if 'identifier' in kwargs:
            instance_id_ = kwargs['identifier'].id
            header_ = kwargs['identifier'].header
            assert self.get_type() == kwargs['identifier'].type
        else:
            instance_id_ = kwargs['id'] if 'id' in kwargs \
                                        else str(uuid.uuid4())
            header_ = kwargs['header'] if 'header' in kwargs else \
                semantic_manager_.get_default_header()

        # old_state_ = kwargs['old_state'] if 'old_state' in kwargs else None

        identifier_ = InstanceIdentifier(
                        id=instance_id_,
                        type=self.get_type(),
                        header=header_,
                    )

        if 'enforce_new' in kwargs:
            enforce_new = kwargs['enforce_new']
        else:
            enforce_new = False

        # test if this instance was taken out of the instance_registry instead
        # of being newly created. If yes abort __init__(), to prevent state
        # overwrite !
        if not enforce_new:
            if semantic_manager_.does_instance_exists(identifier_):
                return

        super().__init__(id=instance_id_,
                         header=header_,
                         semantic_manager=semantic_manager_,
                         references={})

        semantic_manager_.instance_registry.register(self)

    def are_rule_fields_valid(self) -> bool:
        """
        Test if all fields are valid

        Returns:
            bool, True if all valid
        """
        return len(self.get_invalid_fields()) == 0

    def get_invalid_fields(self) -> List[Field]:
        """
        Get all fields that are currently not valid

        Returns:
            List[Field]
        """
        return [f for f in self.get_rule_fields() if not f.is_valid()]

    def get_rule_fields(self) -> List[Field]:
        """
        Get all RuleFields of class

        Returns:
            List[Field]
        """
        res: List[Field] = self.get_relation_fields()
        res.extend(self.get_data_fields())
        return res

    def get_type(self) -> str:
        """
        Get _internal_type as used in Fiware, equal to class name

        Returns:
            str
        """
        return self._get_class_name()

    def _get_class_name(self) -> str:
        """
        Get name of class

        Returns:
            str
        """
        return type(self).__name__

    def delete(self, assert_no_references: bool = False):

        if assert_no_references:
            assert len(self.references) == 0

        # remove all notes in other instances that they are referenced
        # clear all field data, this automatically handles the references
        for field in self.get_fields():
            field.clear()

        # remove all references in other instances
        for identifier, field_names in self.references.copy().items():
            for field_name in field_names:
                if not self.semantic_manager.was_instance_deleted(identifier):
                    instance = self.semantic_manager.get_instance(identifier)
                    instance.get_field_by_name(field_name).remove(self)

        self.semantic_manager.instance_registry.delete(self)

    def get_fields(self) -> List[Field]:
        """
        Get all fields of class

        Returns:
            List[Field]
        """
        fields: List[Field] = self.get_relation_fields()
        fields.extend(self.get_data_fields())
        return fields

    # def get_field_names(self) -> List[str]:
    #     """
    #     Get names of all fields of class
    #
    #     Returns:
    #         List[str]
    #     """
    #     return [f.name for f in self.get_fields()]

    def get_relation_fields(self) -> List[RelationField]:
        """
        Get all RelationFields of class

        Returns:
           List[RelationField]
        """
        relationships = []
        for key, value in self.__dict__.items():
            if isinstance(value, RelationField):
                rel: RelationField = value
                relationships.append(rel)
        return relationships

    def get_data_fields(self) -> List[DataField]:
        """
        Get all DataFields of class

        Returns:
          List[DataField]
        """
        fields = []
        for key, value in self.__dict__.items():
            if isinstance(value, DataField):
                fields.append(value)
        return fields

    def get_relation_field_names(self) -> List[str]:
        """
        Get names of all RelationFields of class

        Returns:
            List[str]
        """
        return [f.name for f in self.get_relation_fields()]

    def get_data_field_names(self) -> List[str]:
        """
        Get names of all DataFields of class

        Returns:
            List[str]
        """
        return [f.name for f in self.get_data_fields()]

    def get_field_by_name(self, field_name: str) -> Field:
        """
        Get a field of class by its property name

        Raises:
            KeyError: If name does not belong to a field
        Returns:
            Field
        """
        for key, value in self.__dict__.items():
            if isinstance(value, Field):
                if value.name == field_name:
                    return value

        raise KeyError(f'{field_name} is not a valid Field for class '
                       f'{self._get_class_name()}')

    def build_context_entity(self) -> ContextEntity:
        """
        Convert the instance to a ContextEntity that contains all fields as
        NamedContextAttribute

        Returns:
            ContextEntity
        """

        entity = ContextEntity(
            id=self.id,
            type=self._get_class_name()
        )

        for field in self.get_fields():
            entity.add_attributes([field.build_context_attribute()])

        reference_str_dict = \
            {identifier.json(): value
             for (identifier, value) in self.references.items()}

        # add meta attributes
        entity.add_attributes([
            NamedContextAttribute(
                name="__references",
                type=DataType.STRUCTUREDVALUE,
                value=reference_str_dict
            )
        ])

        return entity

    def get_identifier(self) -> InstanceIdentifier:
        """
        Get identifier of instance, each instance's identifier is unique

        Returns:
            str
        """
        return InstanceIdentifier(id=self.id, type=self.get_type(),
                                  header=self.header)

    def get_all_field_names(self) -> List[str]:
        res = []
        for field in self.get_fields():
            res.extend(field.get_field_names())
        return res

    class Config:
        """
        Forbid manipulation of class

        No Fields can be added/removed

        The identifier can not be changed
        """
        arbitrary_types_allowed = True
        allow_mutation = False
        underscore_attrs_are_private = True

    def __str__(self):
        return str(self.dict(exclude={'semantic_manager', 'old_state'}))


T = TypeVar('T')


# class ProtectedProperty(Generic[T], BaseModel):
#     _value: T = None
#
#     def __init__(self, default_value: T = None, **data: Any):
#         super().__init__(**data)
#         self._value = default_value
#
#     def get(self) -> T:
#         return self._value
#
#     def set(self, value: T):
#         self._value = value
#
#     class Config:
#         underscore_attrs_are_private = True

class DeviceSettings(BaseModel):
    transport: Optional[TransportProtocol]
    endpoint: Optional[AnyHttpUrl]
    apikey: Optional[str]
    protocol: Optional[str]
    timezone: Optional[str]
    timestamp: Optional[bool]
    expressionLanguage: Optional[ExpressionLanguage]
    explicitAttrs: Optional[bool]

    class Config:
        validate_assignment=True

class SemanticDeviceClass(SemanticClass):

    # old_device_state: Optional[ContextDevice]
    """needed ?"""

    # Used an internal dict to bypass objects immutability

    # transport: ProtectedProperty[TransportProtocol] = ProtectedProperty()
    # endpoint: ProtectedProperty[AnyHttpUrl] = ProtectedProperty()
    # apikey: ProtectedProperty[str] = ProtectedProperty()
    # protocol: ProtectedProperty[str] = ProtectedProperty()
    # timezone: ProtectedProperty[str] = ProtectedProperty()
    # timestamp: ProtectedProperty[bool] = ProtectedProperty()
    # expressionLanguage: ProtectedProperty[ExpressionLanguage] = \
    #     ProtectedProperty()
    # explicitAttrs: ProtectedProperty[bool] = ProtectedProperty(False)

    device_settings: DeviceSettings = DeviceSettings()

    def delete(self, assert_no_references: bool = False):
        #todo
        pass

    def get_fields(self) -> List[Field]:
        """
        Get all fields of class

        Returns:
            List[str]
        """
        res = []
        for key, value in self.__dict__.items():
            if isinstance(value, Field):
                res.append(value)
        return res

    def get_command_fields(self) -> List[CommandField]:
        """
        Get all CommandFields of class

        Returns:
           List[CommandField]
        """
        commands = []
        for key, value in self.__dict__.items():
            if isinstance(value, CommandField):
                commands.append(value)
        return commands

    def get_device_attribute_fields(self) -> List[DeviceAttributeField]:
        """
        Get all DeviceAttributeField of class

        Returns:
          List[DeviceAttributeField]
        """
        fields = []
        for key, value in self.__dict__.items():
            if isinstance(value, DeviceAttributeField):
                fields.append(value)
        return fields

    def get_command_field_names(self) -> List[str]:
        """
        Get names of all CommandFields of class

        Returns:
            List[str]
        """
        return [f.name for f in self.get_command_fields()]

    def get_device_attribute_field_names(self) -> List[str]:
        """
        Get names of all DeviceAttributeFields of class

        Returns:
            List[str]
        """
        return [f.name for f in self.get_device_attribute_fields()]

    # def get_property_dict(self) -> Dict[str, ProtectedProperty]:
    #     """
    #     Get all DeviceAttributeField of class
    #
    #     Returns:
    #       List[DeviceAttributeField]
    #     """
    #     res = {}
    #     for key, value in self.__dict__.items():
    #         if isinstance(value, ProtectedProperty):
    #             res[key] = value.get()
    #     return res

    # needed when saving local state
    def build_context_entity(self) -> ContextEntity:
        entity = super(SemanticDeviceClass, self).build_context_entity()

        entity.add_attributes([
            NamedContextAttribute(
                name="__device_settings",
                type=DataType.STRUCTUREDVALUE,
                value=self.device_settings.dict()
            )
        ])
        return entity

    def build_context_device(self) -> iot.Device:
        """
        Convert the instance to a ContextEntity that contains all fields as
        NamedContextAttribute

        Returns:
            ContextEntity
        """
        device = iot.Device(
            device_id=f'{self.id}',
            service=self.header.service,
            service_path=self.header.service_path,
            entity_name=self.id,
            entity_type=self._get_class_name(),
            apikey=self.device_settings.apikey,
            endpoint=self.device_settings.endpoint,
            protocol=self.device_settings.protocol,
            transport=self.device_settings.transport,
            timestamp=self.device_settings.timestamp,
            expressionLanguage=self.device_settings.expressionLanguage,
            ngsiVersion=self.header.fiware_version
        )

        for field in self.get_fields():
            for attr in field.build_device_attributes():
                device.add_attribute(attr)

        reference_str_dict = \
            {identifier.json(): value
             for (identifier, value) in self.references.items()}


        # add meta attributes
        device.add_attribute(
            iot.StaticDeviceAttribute(
                name="__references",
                type=DataType.STRUCTUREDVALUE,
                value=reference_str_dict,
                entity_name=None,
                entity_type=None,
                reverse=None,
                expression=None,
                metadata=None
            )
        )

        device.add_attribute(
            iot.StaticDeviceAttribute(
                name="__device_settings",
                type=DataType.STRUCTUREDVALUE,
                value=self.device_settings.dict(),
                entity_name=None,
                entity_type=None,
                reverse=None,
                expression=None,
                metadata=None
            )
        )

        return device




class SemanticIndividual(BaseModel):
    """
    A class representing a vocabulary/ontology Individual.
    A Individual has no fields and no values can be assigned

    It functions as some kind of enum value that can be inserted in
    RelationFields

    Each instance of an SemanticIndividual Class is equal
    """

    _parent_classes: List[type]
    """List of ontology parent classes needed to validate RelationFields"""

    def __eq__(self, other):
        """Each instance of an SemanticIndividual Class is equal"""
        return type(self) == type(other)

    def __str__(self):
        return type(self).__name__

    def get_name(self):
        """
        Get the name of the class

        Returns:
            str
        """
        return type(self).__name__

    def is_instance_of_class(self, class_: type) -> False:
        """
        Test if the individual is an instance of a class.

        Args:
            class_ (type): Class to be checked against

        Returns:
            bool, True if individual is of the searched class or one its parents
        """

        if isinstance(self, class_):
            return True
        for parent in self._parent_classes:
            if isinstance(parent(), class_):
                return True
        return False



