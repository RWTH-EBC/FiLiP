import collections
import uuid
from enum import Enum
from typing import List, Tuple, Dict, Type, TYPE_CHECKING, Optional, Union

import requests

from filip.models.ngsi_v2.iot import ExpressionLanguage, TransportProtocol
import filip.models.ngsi_v2.iot as iot
from filip.models.base import DataType, NgsiVersion

from filip.models.ngsi_v2.context import ContextEntity, NamedContextAttribute


from filip.models import FiwareHeader
from pydantic import BaseModel, Field, AnyHttpUrl
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
        use_enum_values = True


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
    """If Type==String: Blacklisted chars; if empty none are forbidden"""
    allowed_chars: List[str]
    """If Type==String: Whitelisted chars; if empty all chars are allowed"""
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
                except ValueError:
                    return False
            else:
                try:
                    number = int(value)
                except ValueError:
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


class DevicePropertyInstanceLink(BaseModel):
    instance_identifier: Optional[InstanceIdentifier] = None
    """Identifier of the instance holding this Property"""
    semantic_manager: Optional['SemanticManager'] = None
    """Link to the governing semantic_manager"""
    field_name: Optional[str] = None
    """Name of the field to which this property was added in the instance"""


class DeviceProperty(BaseModel):
    """
    Model describing one specific property of an IoT device.
    It is either a command that can be executed or an attribute that can be read

    A property can only belong to one field of one instance. Assigning it to
    multiple fields will result in an error.
    """

    name: str
    """Internally used name in the IoT Device"""
    _instance_link: DevicePropertyInstanceLink = DevicePropertyInstanceLink()
    # _instance_identifier: Optional[InstanceIdentifier] = None
    # """Identifier of the instance holding this Property"""
    # _semantic_manager: Optional['SemanticManager'] = None
    # """Link to the governing semantic_manager"""
    # _field_name: Optional[str] = None
    # """Name of the field to which this property was added in the instance"""

    def _get_instance(self) -> 'SemanticClass':
        """Get the instance object to which this property was added"""

        return self._instance_link.semantic_manager.get_instance(
            self._instance_link.instance_identifier)

    def _get_field_from_fiware(self, field_name: str, required_type: str) \
            -> NamedContextAttribute:
        """
        Retrieves live information about a field from the assigned instance
        from Fiware

        Args:
            field_name (str): Name of the to retrieving field
            required_type (str): Type that the retrieved field is required to
                                 have
        Raises:
            Exception;  if the instance or the field is not present in Fiware
                        (the instance  state was not yet saved)
            Exception;  The field_type does not match
        """

        if self._instance_link.field_name is None:
            raise Exception("This DeviceProperty needs to be added to a "
                            "device field of an SemanticDeviceClass instance "
                            "and the state saved before this methode can be "
                            "executed")

        try:
            entity = self._instance_link.semantic_manager.\
                get_entity_from_fiware(
                    instance_identifier=self._instance_link.instance_identifier)
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
        return attr

    def get_all_field_names(self) -> List[str]:
        """
        Get all field names which this property creates in the fiware
        instance
        """
        pass

    class Config:
        underscore_attrs_are_private = True


class Command(DeviceProperty):
    """
    Model describing a command property of an IoT device.

    The command will add three fields to the fiware instance:
        - name - Used to execute the command, function: send()
        - name_info - Used to retrieve the command result: get_info()
        - name_status - Used to see the current status: get_status()

    A command can only belong to one field of one instance. Assigning it to
    multiple fields will result in an error.
    """

    def send(self):
        """
        Execute the command on the IoT device

        Raises:
            Exception: If the command was not yet saved to Fiware
        """
        attr = self._get_field_from_fiware(field_name=self.name,
                                           required_type="command")
        client = self._instance_link.semantic_manager.get_client(
                 self._instance_link.instance_identifier.header)

        client.update_entity_attribute(
            entity_id=self._instance_link.instance_identifier.id,
            attr=attr)
        client.close()

    def get_info(self) -> str:
        """
        Retrieve the executed command result from the IoT-Device

        Raises:
            Exception: If the command was not yet saved to Fiware
        """
        return self._get_field_from_fiware(field_name=f'{self.name}_info',
                                           required_type="commandResult").value

    def get_status(self):
        """
        Retrieve the executed command status from the IoT-Device

        Raises:
            Exception: If the command was not yet saved to Fiware
        """
        return self._get_field_from_fiware(field_name=f'{self.name}_status',
                                           required_type="commandStatus").value

    def get_all_field_names(self) -> List[str]:
        """
        Get all the field names that this command will add to Fiware
        """
        return [self.name, f"{self.name}_info", f"{self.name}_result"]

    class Config:
        """if the name is changed the attribute needs to be removed
        and re-added to the device. With frozen that logic is more clearly
        given in the library. Further it allows us to hash the object"""
        frozen = True


class DeviceAttributeType(str, Enum):
    """
    Retrieval type of the DeviceAttribute value from the IoT Device into Fiware
    """
    lazy = "lazy"
    """The value is only read out if it is requested"""
    active = "active"
    """The value is kept up-to-date"""


class DeviceAttribute(DeviceProperty):
    """
    Model describing an attribute property of an IoT device.

    The attribute will add one field to the fiware instance:
        - {NameOfInstanceField}_{Name}, holds the value of the Iot device
        attribute: get_value()

    A DeviceAttribute can only belong to one field of one instance. Assigning
    it to multiple fields will result in an error.
    """
    attribute_type: DeviceAttributeType
    """States if the attribute is read actively or lazy from the IoT Device 
    into Fiware"""

    def get_value(self):
        """
        Retrieve the current value from the Iot Device

        Raises:
            Exception: If the DeviceAttribute was not yet saved to Fiware
        """
        return self._get_field_from_fiware(
            field_name=f'{self._instance_link.field_name}_{self.name}',
            required_type="StructuredValue").value

    def get_all_field_names(self) -> List[str]:
        """
        Get all the field names that this command will add to Fiware
        """
        return [f'{self._instance_link.field_name}_{self.name}']

    class Config:
        """if the name or type is changed the attribute needs to be removed
        and readded to the device. With frozen that logic is more clearly
        given in the library. Further it allows us to hash the object"""
        frozen = True
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
    """Internal list of the field, to which values are saved"""

    def __init__(self,  name, semantic_manager):
        self._semantic_manager = semantic_manager
        super().__init__()
        self.name = name
        self._list = list()

    def is_valid(self) -> bool:
        """
        Check if the current state is valid -> Can be saved to Fiware
        """
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
        """
        Convert the field to a DeviceAttribute that can eb added to a
        DeviceEntity

        Returns:
            List[Union[iot.DeviceAttribute,
                       iot.LazyDeviceAttribute,
                       iot.StaticDeviceAttribute,
                       iot.DeviceCommand]]
        """
        values = []
        for v in self.get_all_raw():
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
        values = self.get_all_raw()
        for value in values:
            result += f'{value}, '
        if len(values) > 0:
            result = result[:-2]
        return result

    def get_all_raw(self) -> List:
        """
        Get all values of the field exactly as they are hold inside the
        internal list
        """
        return self._list
    
    def get_all(self) -> List:
        """
        Get all values of the field in usable form
        """
        return [self.__getitem__(i) for i in range(len(self._list))]

    def _get_instance(self) -> 'SemanticClass':
        """
        Get the instance object to which this field belongs
        """
        return self._semantic_manager.get_instance(self._instance_identifier)

    def get_field_names(self) -> List[str]:
        """
        Get the names of all fields this field will create in the Fiware entity.
        (DeviceProperties can create additional fields)

        Returns:
            List[str]
        """
        return [self.name]

    def values_to_json(self) -> List[str]:
        """
        Convert each value of the field to a json string

        Returns:
            List[str]
        """
        res = []
        for v in self.get_all_raw():
            if isinstance(v, BaseModel):
                res.append(v.json())
            else:
                res.append(v)
        return res

    class Config:
        underscore_attrs_are_private = True


class DeviceField(Field):

    _internal_type: type = DeviceProperty
    """
    Type which is allowed to be stored in the field.
    Set in the subclasses, but has to be a subclass of DeviceProperty
    """

    def is_valid(self) -> bool:
        """
        Check if the current state is valid -> Can be saved to Fiware

        Returns:
            True, if all values are of type _internal_type
        """
        for value in self.get_all_raw():
            if not isinstance(value, self._internal_type):
                return False
        return True

    def _pre_set(self, v):
        """
        Executes checks before value v is assigned to field values
        And sets internal values of v to link it to this field

        Args:
             v (Any): Value to be added to the field
        Raises:
            AssertionError: if v not of type: internal_type
                            if v does already belong to a field
        """
        assert isinstance(v, self._internal_type)
        assert v._instance_link.instance_identifier is None, "DeviceProperty can only " \
                                               "belong to one device instance"
        v._instance_link.instance_identifier = self._instance_identifier
        v._instance_link.semantic_manager = self._semantic_manager
        v._instance_link.field_name = self.name

    def _name_check(self, v: _internal_type):
        """
        Executes name checks before value v is assigned to field values
        Each field name that v will add to the Fiware instance needs to be
        available

        Args:
            v (_internal_type): Value to be added to the field
        Raises:
            NameError: if a field name of v is not available
                       if a field name of v is blacklisted
                       if the name of v contains a forbidden character
        """
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
        """List function: Remove a values
        Makes the value available again to be added to other fields/instances
        """
        v = self._list[i]
        v._instance_link.instance_identifier = None
        v._instance_link.semantic_manager = None
        v._instance_link.field_name = None
        del self._list[i]
        
    def __setitem__(self, i, v):
        """List function: If checks pass , add value
        """
        self._name_check(v)
        self._pre_set(v)
        super(DeviceField, self).__setitem__(i, v)
        
    def insert(self, i, v):
        """List function: If checks pass , add value at position i
        """
        self._name_check(v)
        self._pre_set(v)
        super(DeviceField, self).insert(i, v)

    def get_field_names(self) -> List[str]:
        names = super().get_field_names()
        for v in self.get_all_raw():
            names.extend(v.get_all_field_names())
        return names

    def build_context_attribute(self) -> NamedContextAttribute:
        """only needed when saving local state as json"""
        values = []
        for v in self.get_all_raw():
            if isinstance(v, BaseModel):
                values.append(v.dict())
            else:
                values.append(v)
        return NamedContextAttribute(name=self.name, value=values)


class CommandField(DeviceField):

    _internal_type = Command

    def get_all_raw(self) -> List[Command]:
        return super().get_all_raw()

    def __getitem__(self, i) -> Command:
        return super(CommandField, self).__getitem__(i)

    def build_device_attributes(self) -> List[Union[iot.DeviceAttribute,
                                                    iot.LazyDeviceAttribute,
                                                    iot.StaticDeviceAttribute,
                                                    iot.DeviceCommand]]:
        attrs = super().build_device_attributes()
        for command in self.get_all_raw():
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

    def get_all_raw(self) -> List[DeviceAttribute]:
        return super().get_all_raw()

    def build_device_attributes(self) -> List[Union[iot.DeviceAttribute,
                                                    iot.LazyDeviceAttribute,
                                                    iot.StaticDeviceAttribute,
                                                    iot.DeviceCommand]]:
        attrs = super().build_device_attributes()

        for attribute in self.get_all_raw():

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
            value=[v for v in self.get_all_raw()]
        )

    def __setitem__(self, i, v):
        if isinstance(v, Enum):
            self._list[i] = v.value
        else:
            self._list[i] = v

    def insert(self, i, v):
        if isinstance(v, Enum):
            self._list.insert(i, v.value)
        else:
            self._list.insert(i, v)

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
    inverse_of: List[str] = []
    """List of all field names which are inverse to this field.
    If an instance i1 is added to this field, the instance i2 belonging to this 
    field is added to all fields of i1 that are stated in this list by name"""

    def __init__(self, rule, name, semantic_manager, inverse_of=None):
        super().__init__(rule, name, semantic_manager)
        self.inverse_of = inverse_of

    def _value_is_valid(self, value, rule_value: type) -> bool:
        if isinstance(value, SemanticClass):
            return isinstance(value, rule_value)
        elif isinstance(value, SemanticIndividual):
            value.is_instance_of_class(rule_value)
            return value.is_instance_of_class(rule_value)
        else:
            return False

    def build_context_attribute(self) -> NamedContextAttribute:
        values = []
        for v in self.get_all_raw():
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
        elif isinstance(v, str):
            return self._semantic_manager.get_individual(v)

    def __setitem__(self, i, v: Union['SemanticClass', 'SemanticIndividual']):
        """ see class description
        Raises:
            AttributeError: if value not an instance of 'SemanticClass' or
            'SemanticIndividual'
        """
        self._uniqueness_check(v)

        if isinstance(v, SemanticClass):
            self._list[i] = v.get_identifier()
            v.add_reference(self._instance_identifier, self.name)

            self._add_inverse(v)
        elif isinstance(v, SemanticIndividual):
            self._list[i] = v.get_name()
        else:
            raise AttributeError("Only instances of a SemanticClass or a "
                                 "SemanticIndividual can be given as value")

    def __delitem__(self, i):
        """ see class description"""
        if isinstance(self._list[i], InstanceIdentifier):

            # delete reference
            if not self._semantic_manager.was_instance_deleted(self._list[i]):
                v: SemanticClass = \
                    self._semantic_manager.get_instance(self._list[i])
                v.remove_reference(self._instance_identifier, self.name)

            # delete value in field
            identifier = self._list[i]
            del self._list[i]

            # inverse of deletion
            if not self._semantic_manager.was_instance_deleted(identifier):
                # remove this instance in reverse fields
                if self.inverse_of is not None:
                    for inverse_field_name in self.inverse_of:
                        if inverse_field_name in v.get_all_field_names():
                            field = v.get_field_by_name(inverse_field_name)
                            if self._instance_identifier in field.get_all_raw():
                                field.remove(self._get_instance())
        else:
            del self._list[i]

    def insert(self, i, v: Union['SemanticClass', 'SemanticIndividual']):
        """ see class description
        Raises:
            AttributeError: if value not an instance of 'SemanticClass' or
            'SemanticIndividual'
        """
        self._uniqueness_check(v)
        if isinstance(v, SemanticClass):
            identifier = v.get_identifier()
            self._list.insert(i, identifier)
            v.add_reference(self._instance_identifier, self.name)
            self._add_inverse(v)
        elif isinstance(v, SemanticIndividual):
            self._list.insert(i, v.get_name())
        else:
            raise AttributeError("Only instances of a SemanticClass or a "
                                 "SemanticIndividual can be given as value")

    def _add_inverse(self, v: 'SemanticClass'):
        if self.inverse_of is not None:
            for inverse_field_name in self.inverse_of:
                if inverse_field_name in v.get_all_field_names():
                    field = v.get_field_by_name(inverse_field_name)
                    if self._instance_identifier not in field.get_all_raw():
                        field.append(self._get_instance())

    def _uniqueness_check(self, v):
        if isinstance(v, SemanticClass):
            if v.get_identifier() in self.get_all_raw():
                raise ValueError("Value already added")
        else:
            if v in self.get_all_raw():
                raise ValueError("Value already added")

    def __str__(self):
        """ see class description"""
        return 'Relation'+super().__str__()

    def get_all(self) -> List[Union['SemanticClass', 'SemanticIndividual']]:
        return super(RelationField, self).get_all()


class InstanceState(BaseModel):
    """State of instance that it had in Fiware on the moment of the last load
    Wrapped in an object to bypass the SemanticClass immutability
    """
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
    """Pointer to the governing semantic_manager"""

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

    def is_valid(self) -> bool:
        """
        Test if instance is valid -> Is correctly defined and can be saved to
        Fiware

        Returns:
            bool
        """
        return self.are_rule_fields_valid()

    def are_rule_fields_valid(self) -> bool:
        """
        Test if all rule fields are valid

        Returns:
            bool, True if all valid
        """
        return len(self.get_invalid_rule_fields()) == 0

    def get_invalid_rule_fields(self) -> List[Field]:
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
        """
        Delete this instance.
        All references made to this instance by other instances will be removed
        On save_state it will also be deleted from Fiware

        Args:
            assert_no_references (bool): If True the instance is not deleted
            and an Error is raised, if some other instance references this
            instance.
        """

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

    def get_fields(self) -> List[RuleField]:
        """
        Get all fields of class

        Returns:
            List[Field]
        """
        fields: List[RuleField] = self.get_relation_fields()
        fields.extend(self.get_data_fields())
        return fields

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
                name="referencedBy",
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


class DeviceSettings(BaseModel):
    """Settings configuring the communication with an IoT Device
    Wrapped in a model to bypass SemanticDeviceClass immutability
    """
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
    """
    A class representing a vocabulary/ontology class.
    A class has predefined fields
    Each instance of a class links to a unique Fiware ContextDevice (by
    Identifier) and represents one IoT Device of the real world.

    If a class is initiated it is first looked if this instance (equal over
    identifier) exists in the local registry. If yes that instance is returned

    If no, it is looked if this instance exists in Fiware, if yes it is
    loaded and returned, else a new instance of the class is initialised and
    returned
    """

    # old_device_state: Optional[ContextDevice]
    """needed ?"""

    device_settings: DeviceSettings = DeviceSettings()
    """Settings configuring the communication with an IoT Device 
    Wrapped in a model to bypass SemanticDeviceClass immutability"""

    def is_valid(self):
        """
        Test if instance is valid -> Is correctly defined and can be saved to
        Fiware

        Returns:
           bool
        """
        return super().is_valid() and self.are_device_settings_valid()

    def are_device_settings_valid(self):
        """
        Test if device settings are valid

        Returns:
             bool, True if endpoint and transport are not None
        """
        return self.device_settings.endpoint is not None and \
            self.device_settings.transport is not None

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

    # needed when saving local state
    def build_context_entity(self) -> ContextEntity:
        entity = super(SemanticDeviceClass, self).build_context_entity()

        entity.add_attributes([
            NamedContextAttribute(
                name="deviceSettings",
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
                name="referencedBy",
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
                name="deviceSettings",
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
            if parent == class_:
                return True
        return False



