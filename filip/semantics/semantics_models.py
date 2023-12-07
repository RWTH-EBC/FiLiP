"""Module containing the models describing a semantic state"""

import uuid

import pydantic as pyd
import requests
from aenum import Enum
from typing import List, Tuple, Dict, Type, TYPE_CHECKING, Optional, Union, \
    Set, Iterator, Any

import filip.models.ngsi_v2.iot as iot
# from filip.models.ngsi_v2.iot import ExpressionLanguage, TransportProtocol
from filip.models.base import DataType, NgsiVersion
from filip.utils.validators import FiwareRegex
from filip.models.ngsi_v2.context import ContextEntity, NamedContextAttribute, \
    NamedCommand

from filip.models import FiwareHeader
from pydantic import ConfigDict, BaseModel, Field
from filip.config import settings
from filip.semantics.vocabulary.entities import DatatypeFields, DatatypeType
from filip.semantics.vocabulary_configurator import label_blacklist, \
    label_char_whitelist

if TYPE_CHECKING:
    from filip.semantics.semantics_manager import SemanticsManager


class InstanceHeader(FiwareHeader):
    """
    Header of a SemanticClass instance, describes the Fiware Location were
    the instance will be / is saved.
    The header is not bound to one Fiware Setup, but can describe the
    exact location in the web
    """
    model_config = ConfigDict(frozen=True, use_enum_values=True)
    cb_url: str = Field(default=settings.CB_URL,
                        description="Url of the ContextBroker from the Fiware "
                                    "setup")
    iota_url: str = Field(default=settings.IOTA_URL,
                          description="Url of the IoTABroker from the Fiware "
                                      "setup")

    ngsi_version: NgsiVersion = Field(default=NgsiVersion.v2,
                                      description="Used Version in the "
                                                  "Fiware setup")

    def get_fiware_header(self) -> FiwareHeader:
        """
        Get a Filip FiwareHeader from the InstanceHeader
        """
        return FiwareHeader(service=self.service,
                            service_path=self.service_path)


class InstanceIdentifier(BaseModel):
    """
    Each Instance of a SemanticClass posses a unique identifier that is
    directly linked to one Fiware entry
    """
    model_config = ConfigDict(frozen=True)
    id: str = Field(description="Id of the entry in Fiware")
    type: str = Field(description="Type of the entry in Fiware, equal to "
                                  "class_name")
    header: InstanceHeader = Field(description="describes the Fiware "
                                               "Location were the instance "
                                               "will be / is saved.")


class Datatype(DatatypeFields):
    """
    Model of a vocabulary/ontology Datatype used to validate assignments in
    DataFields
    """

    def value_is_valid(self, value: str) -> bool:
        """
        Test if value is valid for this datatype.
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
    """
    SubProperties of a DeviceProperty, containing the information to which
    instance the DeviceProperty belongs.

    Modeled as a standalone model, to bypass the read-only logic of
    DeviceProperty
    """
    instance_identifier: Optional[InstanceIdentifier] = Field(
        default=None,
        description="Identifier of the instance holding this Property")
    semantic_manager: Optional['SemanticsManager'] = Field(
        default=None,
        description="Link to the governing semantic_manager")
    field_name: Optional[str] = Field(
        default=None,
        description="Name of the field to which this property was added "
                    "in the instance")


class DeviceProperty(BaseModel):
    """
    Model describing one specific property of an IoT device.
    It is either a command that can be executed or an attribute that can be read

    A property can only belong to one field of one instance. Assigning it to
    multiple fields will result in an error.
    """
    model_config = ConfigDict()

    name: str = Field("Internally used name in the IoT Device")
    _instance_link: DevicePropertyInstanceLink = DevicePropertyInstanceLink()
    """Additional properties describing the instance and field where this \
    property was added"""

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
            entity = self._instance_link.semantic_manager. \
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

    def get_all_field_names(self, field_name: Optional[str] = None) \
            -> List[str]:
        """
        Get all field names which this property creates in the fiware
        instance

        Args:
            field_name (Optional[str]): Name of the field to which the attribute
                is/will be added. If none is provided, the linked field name
                is used
        """
        pass


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
    model_config = ConfigDict(frozen=True)

    def send(self):
        """
        Execute the command on the IoT device

        Raises:
            Exception: If the command was not yet saved to Fiware
        """
        client = self._instance_link.semantic_manager.get_client(
            self._instance_link.instance_identifier.header)

        context_command = NamedCommand(name=self.name, value="")
        identifier = self._instance_link.instance_identifier
        client.post_command(entity_id=identifier.id,
                            entity_type=identifier.type,
                            command=context_command)
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

    def get_all_field_names(self, field_name: Optional[str] = None) \
            -> List[str]:
        """
        Get all the field names that this command will add to Fiware

        Args:
            field_name (Optional[str]): Not used, but needed in the signature
        """
        return [self.name, f"{self.name}_info", f"{self.name}_result"]


class DeviceAttributeType(str, Enum):
    """
    Retrieval type of the DeviceAttribute value from the IoT Device into Fiware
    """
    _init_ = 'value __doc__'

    lazy = "lazy", "The value is only read out if it is requested"
    active = "active", "The value is kept up-to-date"


class DeviceAttribute(DeviceProperty):
    """
    Model describing an attribute property of an IoT device.

    The attribute will add one field to the fiware instance:
    - {NameOfInstanceField}_{Name}, holds the value of the Iot device
    attribute: get_value()

    A DeviceAttribute can only belong to one field of one instance. Assigning
    it to multiple fields will result in an error.
    """
    model_config = ConfigDict(frozen=True, use_enum_values=True)
    attribute_type: DeviceAttributeType = Field(
        description="States if the attribute is read actively or lazy from "
                    "the IoT Device into Fiware"
    )

    def get_value(self):
        """
        Retrieve the current value from the Iot Device

        Raises:
            Exception: If the DeviceAttribute was not yet saved to Fiware
        """
        return self._get_field_from_fiware(
            field_name=f'{self._instance_link.field_name}_{self.name}',
            required_type="StructuredValue").value

    def get_all_field_names(self, field_name: Optional[str] = None) \
            -> List[str]:
        """
        Get all field names which this property creates in the fiware
        instance

        Args:
            field_name (str): Name of the field to which the attribute
                is/will be added. If none is provided, the linked field name
                is used
        """
        if field_name is None:
            field_name = self._instance_link.field_name
        return [f'{field_name}_{self.name}']


class Field(BaseModel):
    """
    A Field corresponds to a CombinedRelation for a class from the vocabulary.
    It itself is a _set, that is enhanced with methods to provide validation
    of the values according to the rules stated in the vocabulary.

    The values of a field are unique and without order

    The fields of a class are predefined. A field can contain standard values
    on init
    """
    model_config = ConfigDict()

    name: str = Field(
        default="",
        description="Name of the Field, corresponds to the property name that "
                    "it has in the SemanticClass")

    _semantic_manager: 'SemanticsManager'
    "Reference to the global SemanticsManager"

    _instance_identifier: InstanceIdentifier
    "Identifier of instance, that has this field as property"

    _set: Set = Field(
        default=set(),
        description="Internal set of the field, to which values are saved")

    def __init__(self, name, semantic_manager):
        self._semantic_manager = semantic_manager
        super().__init__()
        self.name = name
        self._set = set()

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
                values.append(v.model_dump())
            else:
                values.append(v)

        x = [
            iot.StaticDeviceAttribute(
                name=self.name,
                type=DataType.STRUCTUREDVALUE,
                value=values,
                entity_name=None,
                entity_type=None
            )
        ]

        return x

    def __len__(self) -> int:
        """Get the number of values

        Returns:
            int
        """
        return len(self._set)

    def size(self) -> int:
        """Get the number of values

        Returns:
            int
        """
        return self.__len__()

    def remove(self, v):
        """
        Remove the given value from the field.

        Args:
            v, value that is in the field

        Raises:
            KeyError: if value not in field
        """
        self._set.remove(v)

    def add(self, v):
        """
        Add the value v to the field, duplicates are ignored (Set logic)

        Args:
            v (Any) Value to be added, of fitting type
        Raises:
            ValueError: if v is of invalid type
        """
        self._set.add(v)

    def update(self, values: Union[List, Set]):
        """
        Add all the values to the field, duplicates are ignored (Set logic)

        Args:
            values (Union[List, Set]): Values to be added, each of fitting type
        Raises:
            ValueError: if one value is of invalid type
        """
        for v in values:
            self.add(v)

    def set(self, values: List):
        """
        Set the values of the field equal to the given list

        Args:
            values: List of values fitting for the field

        Returns:
            None
        """
        self.clear()
        for v in values:
            self.add(v)

    def clear(self):
        """
        Remove all values of the field

        Returns:
            None
        """
        for v in self.get_all():
            self.remove(v)

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

    def get_all_raw(self) -> Set:
        """
        Get all values of the field exactly as they are hold inside the
        internal list
        """
        return self._set

    def get_all(self) -> List:
        """
        Get all values of the field in usable form.
        Returns the set in List for as some values are not hashable in
        converted form.
        But the order is random

        Returns:
            List, unsorted
        """
        return [self._convert_value(v) for v in self._set]

    def _convert_value(self, v):
        """
        Converts the internal saved value v, to the type that should be returned
        """
        return v

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
                res.append(v.model_dump_json())
            else:
                res.append(v)
        return res

    def __contains__(self, item) -> bool:
        """
        Overrides the magic "in" to test if a value/item is inside the field.

        Returns:
            bool
        """
        return item in self.get_all()

    def __iter__(self) -> Iterator[Any]:
        """
        Overrides the magic "in" to loop over the field values
        """
        return self.get_all().__iter__()


class DeviceField(Field):
    """
    A Field that represents a logical part of a device.
    Abstract Superclass
    """

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

    def name_check(self, v: _internal_type):
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
        for name in v.get_all_field_names(field_name=self.name):
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

    def remove(self, v):
        """List function: Remove a values
        Makes the value available again to be added to other fields/instances
        """
        v._instance_link.instance_identifier = None
        v._instance_link.semantic_manager = None
        v._instance_link.field_name = None
        super(DeviceField, self).remove(v)

    def add(self, v):
        """List function: If checks pass , add value

        Args:
            v, value to add

        Raises:
            AssertionError, if v is of wrong type
            AssertionError, if v already belongs to a field
            NameError, if v has an invalid name

        Returns:
            None
        """

        # assert that the given value fulfills certain conditions
        assert isinstance(v, self._internal_type)
        assert isinstance(v, DeviceProperty)
        assert v._instance_link.instance_identifier is None, \
            "DeviceProperty can only belong to one device instance"

        # test if name of v is valid, if not an error is raised
        self.name_check(v)

        # link attribute to field and instance
        v._instance_link.instance_identifier = self._instance_identifier
        v._instance_link.semantic_manager = self._semantic_manager
        v._instance_link.field_name = self.name

        super(DeviceField, self).add(v)

    def get_field_names(self) -> List[str]:
        """
        Get all names of fields that would be/are generated by this field in
        the fiware device_entity and its current values

        Returns:
            List[str]
        """
        names = super().get_field_names()
        for v in self.get_all_raw():
            names.extend(v.get_all_field_names())
        return names

    def build_context_attribute(self) -> NamedContextAttribute:
        """Export Field as NamedContextAttribute

        only needed when saving local state as json

        Returns:
            NamedContextAttribute
        """
        values = []
        for v in self.get_all_raw():
            if isinstance(v, BaseModel):
                values.append(v.model_dump())
            else:
                values.append(v)
        return NamedContextAttribute(name=self.name, value=values)


class CommandField(DeviceField):
    """
     A Field that holds commands that can be send to the device
    """

    _internal_type = Command

    def get_all_raw(self) -> Set[Command]:
        return super().get_all_raw()

    def get_all(self) -> List[Command]:
        return super().get_all()

    def __iter__(self) -> Iterator[Command]:
        return super().__iter__()

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
    """
     A Field that holds attributes of the device that can be referenced for
     live reading of the device
    """
    _internal_type = DeviceAttribute

    def get_all_raw(self) -> Set[DeviceAttribute]:
        return super().get_all_raw()

    def get_all(self) -> List[DeviceAttribute]:
        return super().get_all()

    def __iter__(self) -> Iterator[DeviceAttribute]:
        return super().__iter__()

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
                        entity_type=None
                    )
                )
            else:
                attrs.append(
                    iot.LazyDeviceAttribute(
                        object_id=attribute.name,
                        name=f"{self.name}_{attribute.name}",
                        type=DataType.STRUCTUREDVALUE,
                        entity_name=None,
                        entity_type=None
                    )
                )

        return attrs


class RuleField(Field):
    """
    A RuleField corresponds to a CombinedRelation for a class from the
    vocabulary.
    It itself is a list, that is enhanced with methods to provide validation
    of the values according to the rules stated in the vocabulary

    The fields of a class are predefined. A field can contain standard values
    on init
    """

    _rules: List[Tuple[str, List[List[str]]]]
    """rule formatted for machine readability """
    rule: str = pyd.Field(
        default="",
        description="rule formatted for human readability")

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

        # true if all rules are fulfilled
        for [rule, fulfilled] in self.are_rules_fulfilled():
            if not fulfilled:
                return False
        return True

    def are_rules_fulfilled(self) -> List[Tuple[str, bool]]:
        """
        Check if the values present in this relationship fulfill the
        individual semantic rules.

        Returns:
            List[Tuple[str, bool]], [[readable_rule, fulfilled]]
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

        res = []

        values = self.get_all()
        readable_rules = self.rule.split(",")
        rule_counter = 0

        # loop over all rules, if a rule is not fulfilled return False
        for rule in self._rules:
            # rule has form: (STATEMENT, [[a,b],[c],[a,..],..])
            statement: str = rule[0]
            outer_list: List[List] = rule[1]

            readable_rule = readable_rules[rule_counter].strip()
            rule_counter = rule_counter + 1

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
                    res.append([readable_rule, False])
            elif "max" in statement:
                number = int(statement.split("|")[1])
                if not fulfilling_values <= number:
                    res.append([readable_rule, False])
            elif "exactly" in statement:
                number = int(statement.split("|")[1])
                if not fulfilling_values == number:
                    res.append([readable_rule, False])
            elif "some" in statement:
                if not fulfilling_values >= 1:
                    res.append([readable_rule, False])
            elif "only" in statement:
                if not fulfilling_values == len(values):
                    res.append([readable_rule, False])
            elif "value" in statement:
                if not fulfilling_values >= 1:
                    res.append([readable_rule, False])

            if len(res) == 0 or not (res[-1][0] == readable_rule):
                res.append([readable_rule, True])
        return res

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

    def __str__(self):
        """
        Get Field in a nice readable way

        Returns:
            str
        """
        result = super(RuleField, self).__str__()
        result += f'],\n\trule: ({self.rule})'
        return result

    def _get_all_rule_type_names(self) -> Set[str]:
        """
        Returns the names all types mentioned in the field rule

        Returns:
            Set[str]
        """
        res = set()

        for rule in self._rules:
            statement: str = rule[0]
            outer_list: List[List] = rule[1]
            for inner_list in outer_list:
                for type_name in inner_list:
                    res.add(type_name)
        return res


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

    def add(self, v):
        if isinstance(v, Enum):
            self._set.add(v.value)
        else:
            self._set.add(v)

    def __str__(self):
        return 'Data' + super().__str__()

    def get_possible_enum_values(self) -> List[str]:
        """
        Get all enum values that are excepted for this field

        Returns:
            List[str]
        """
        enum_values = set()
        for type_name in self._get_all_rule_type_names():
            datatype = self._semantic_manager.get_datatype(type_name)
            if datatype.type == DatatypeType.enum:
                enum_values.update(datatype.enum_values)

        return sorted(enum_values)

    def get_all_possible_datatypes(self) -> List[Datatype]:
        """
        Get all Datatypes that are stated as allowed for this field.

        Returns:
            List[Datatype]
        """
        return [self._semantic_manager.get_datatype(type_name)
                for type_name in self._get_all_rule_type_names()]


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
            return value.is_instance_of_class(rule_value)
        else:
            return False

    def build_context_attribute(self) -> NamedContextAttribute:
        values = []
        for v in self.get_all_raw():
            if isinstance(v, InstanceIdentifier):
                values.append(v.model_dump())
            else:
                values.append(v)

        return NamedContextAttribute(
            name=self.name,
            type=DataType.RELATIONSHIP,
            value=values
        )

    def _convert_value(self, v):
        """
        Returns the internal holded objects as SemanticClass or
        SemanticIndividual
        """
        if isinstance(v, InstanceIdentifier):
            return self._semantic_manager.get_instance(v)
        elif isinstance(v, str):
            return self._semantic_manager.get_individual(v)

    def add(self, v: Union['SemanticClass', 'SemanticIndividual']):
        """ see class description
        Raises:
            AttributeError: if value not an instance of 'SemanticClass' or
            'SemanticIndividual'
        """
        # self._uniqueness_check(v)

        if isinstance(v, SemanticClass):
            self._set.add(v.get_identifier())
            v.add_reference(self._instance_identifier, self.name)

            self._add_inverse(v)
        elif isinstance(v, SemanticIndividual):
            self._set.add(v.get_name())
        else:
            raise AttributeError("Only instances of a SemanticClass or a "
                                 "SemanticIndividual can be given as value")

    def remove(self, v):
        """ see class description"""

        if isinstance(v, SemanticClass):
            identifier = v.get_identifier()
            assert identifier in self._set

            # delete reference
            if not self._semantic_manager.was_instance_deleted(identifier):
                v.remove_reference(self._instance_identifier, self.name)

            # delete value in field
            self._set.remove(identifier)

            # inverse of deletion
            if not self._semantic_manager.was_instance_deleted(identifier):
                # remove this instance in reverse fields
                if self.inverse_of is not None:
                    for inverse_field_name in self.inverse_of:
                        if inverse_field_name in v.get_all_field_names():
                            field = v.get_field_by_name(inverse_field_name)
                            if self._instance_identifier in field.get_all_raw():
                                field.remove(self._get_instance())
        elif isinstance(v, SemanticIndividual):
            self._set.remove(v.get_name())
        else:
            raise KeyError(f"v is neither of type SemanticIndividual nor SemanticClass but {type(v)}")

    def _add_inverse(self, v: 'SemanticClass'):
        """
        If a value is added to this field, and this field has an inverse
        logic field bound to it.
        It is tested if the added value posses that field.
        If yes the instance of this field is added to the inverse field of the
        added v
        """
        if self.inverse_of is not None:
            for inverse_field_name in self.inverse_of:
                if inverse_field_name in v.get_all_field_names():
                    field = v.get_field_by_name(inverse_field_name)
                    if self._instance_identifier not in field.get_all_raw():
                        field.add(self._get_instance())

    def __str__(self):
        """ see class description"""
        return 'Relation' + super().__str__()

    def __iter__(self) -> \
            Iterator[Union['SemanticClass', 'SemanticIndividual']]:
        return super().__iter__()

    def get_all(self) -> List[Union['SemanticClass', 'SemanticIndividual']]:
        return super(RelationField, self).get_all()

    def get_all_raw(self) -> Set[Union[InstanceIdentifier, str]]:
        return super().get_all_raw()

    def get_all_possible_classes(self, include_subclasses: bool = False) -> \
            List[Type['SemanticClass']]:
        """
        Get all SemanticClass types that are stated as allowed for this field.

        Args:
            include_subclasses (bool): If true all subclasses of target
                classes are also returned

        Returns:
            List[Type[SemanticClass]]
        """
        res = set()
        for class_name in self._get_all_rule_type_names():
            if class_name.__name__ in self._semantic_manager.class_catalogue:
                class_ = self._semantic_manager. \
                    get_class_by_name(class_name.__name__)
                res.add(class_)
                if include_subclasses:
                    res.update(class_.__subclasses__())

        return list(res)

    def get_all_possible_individuals(self) -> List['SemanticIndividual']:
        """
        Get all SemanticIndividuals that are stated as allowed for this field.

        Returns:
            List['SemanticIndividual']
        """
        res = set()
        for name in self._get_all_rule_type_names():

            if name.__name__ not in self._semantic_manager.class_catalogue:
                res.add(self._semantic_manager.get_individual(name.__name__))
        return list(res)


class InstanceState(BaseModel):
    """State of instance that it had in Fiware on the moment of the last load
    Wrapped in an object to bypass the SemanticClass immutability
    """
    state: Optional[ContextEntity] = None


class SemanticMetadata(BaseModel):
    """
    Meta information about an semantic instance.
    A name and comment that can be used by the user to better identify the
    instance
    """
    model_config = ConfigDict(validate_assignment=True)
    name: str = pyd.Field(default="",
                          description="Optional user-given name for the "
                                      "instance")
    comment: str = pyd.Field(default="",
                             description="Optional user-given comment for "
                                         "the instance")


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
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)
    header: InstanceHeader = pyd.Field(
        description="Header of instance. Holds the information where the "
                    "instance is saved in Fiware")
    id: str = pyd.Field(
        description="Id of the instance, equal to Fiware ContextEntity Id",
        regex=FiwareRegex.standard.value,
    )

    old_state: InstanceState = pyd.Field(
        default=InstanceState(),
        description="State in Fiware the moment the instance was loaded "
                    "in the local registry. Used when saving. "
                    "Only the made changes are reflected")

    references: Dict[InstanceIdentifier, List[str]] = pyd.Field(
        default={},
        description="references made to this instance in other instances "
                    "RelationFields")

    semantic_manager: BaseModel = pyd.Field(
        default=None,
        description="Pointer to the governing semantic_manager, "
                    "vague type to prevent forward ref problems. "
                    "But it will be of type 'SemanticsManager' in runtime")

    metadata: SemanticMetadata = pyd.Field(
        default=SemanticMetadata(),
        description="Meta information about the instance. A name and comment "
                    "that can be used by the user to better identify the "
                    "instance")

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

            import re
            assert re.match(FiwareRegex.standard.value, instance_id), "Invalid character in ID"

            header_ = kwargs['header'] if 'header' in kwargs else \
                semantic_manager_.get_default_header()

        if not instance_id == "" and not enforce_new:

            identifier = InstanceIdentifier(id=instance_id,
                                            type=cls.__name__,
                                            header=header_)

            if semantic_manager_.does_instance_exists(identifier=identifier):
                return semantic_manager_.load_instance(identifier=identifier)

        return super().__new__(cls)

    def __init__(self, *args, **kwargs):
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

    def _build_reference_dict(self) -> Dict:
        """
        Build the reference dict that is set as value in the context entity.
        We need to replace the . as it is a forbidden char for json keys,
        and IPs have .'s.

        The load  _context_entity_to_semantic_class loading teh object back
        again will reverse this swap

        Returns:
            Dict, with . replaced by ---
        """
        return {identifier.json().replace(".", "---"): value
                for (identifier, value) in self.references.items()}

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

        reference_str_dict = self._build_reference_dict()

        # add meta attributes
        entity.add_attributes([
            NamedContextAttribute(
                name="referencedBy",
                type=DataType.STRUCTUREDVALUE,
                value=reference_str_dict
            )
        ])
        entity.add_attributes([
            NamedContextAttribute(
                name="metadata",
                type=DataType.STRUCTUREDVALUE,
                value=self.metadata.model_dump()
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

    def __str__(self):
        return str(self.model_dump(exclude={'semantic_manager', 'old_state'}))

    def __hash__(self):
        values = []
        for field in self.get_fields():
            values.extend((field.name, frozenset(field.get_all_raw())))

        ref_string = ""
        for ref in self.references.values():
            ref_string += f', {ref}'

        return hash((self.id, self.header,
                     self.metadata.name, self.metadata.comment,
                     frozenset(self.references.keys()),
                     ref_string,
                     frozenset(values)
                     ))


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

    device_settings: iot.DeviceSettings = pyd.Field(
        default=iot.DeviceSettings(),
        description="Settings configuring the communication with an IoT Device "
                    "Wrapped in a model to bypass SemanticDeviceClass "
                    "immutability")

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
        return self.device_settings.transport is not None

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
                value=self.device_settings.model_dump()
            )
        ])
        return entity

    def get_device_id(self) -> str:
        return f'{self.get_type()}|{self.id}'

    def build_context_device(self) -> iot.Device:
        """
        Convert the instance to a ContextEntity that contains all fields as
        NamedContextAttribute

        Returns:
            ContextEntity
        """
        device = iot.Device(
            device_id=self.get_device_id(),
            service=self.header.service,
            service_path=self.header.service_path,
            entity_name=f'{self.id}',
            entity_type=self._get_class_name(),
            apikey=self.device_settings.apikey,
            endpoint=self.device_settings.endpoint,
            protocol=self.device_settings.protocol,
            transport=self.device_settings.transport,
            timestamp=self.device_settings.timestamp,
            expressionLanguage=self.device_settings.expressionLanguage,
            ngsiVersion=self.header.ngsi_version
        )

        for field in self.get_fields():
            for attr in field.build_device_attributes():
                device.add_attribute(attr)

        reference_str_dict = self._build_reference_dict()

        # add meta attributes
        device.add_attribute(
            iot.StaticDeviceAttribute(
                name="referencedBy",
                type=DataType.STRUCTUREDVALUE,
                value=reference_str_dict,
            )
        )
        device.add_attribute(
            iot.StaticDeviceAttribute(
                name="metadata",
                type=DataType.STRUCTUREDVALUE,
                value=self.metadata.model_dump()
            )
        )
        device.add_attribute(
            iot.StaticDeviceAttribute(
                name="deviceSettings",
                type=DataType.STRUCTUREDVALUE,
                value=self.device_settings.model_dump(),
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
    model_config = ConfigDict(frozen=True)
    _parent_classes: List[type] = pyd.Field(
        description="List of ontology parent classes needed to validate "
                    "RelationFields"
    )

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
            # to test all subclasses correctly we need to instanciate parent
            # but it needs to be deleted directly again, as it is no real
            # instance that we want to keep in the local state
            parent = parent()
            is_instance = isinstance(parent, class_)
            parent.delete()
            if is_instance:
                return True
        return False
