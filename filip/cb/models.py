from typing import Any, List, Dict, Union, Optional
from pydantic import BaseModel, Field, validator, ValidationError, \
    root_validator, create_model, BaseConfig
from core.models import DataTypes


class ContextMetadata(BaseModel):
    """
    Context metadata is used in FIWARE NGSI in several places, one of them being
    an optional part of the attribute value as described above. Similar to
    attributes, each piece of metadata has:

    Note that in NGSI it is not foreseen that metadata may contain nested
    metadata.
    """
    name: str = Field(
        titel="metadata name",
        description="a metadata name, describing the role of the metadata in the "
                    "place where it occurs; for example, the metadata name "
                    "accuracy indicates that the metadata value describes how "
                    "accurate a given attribute value is. Allowed characters "
                    "are the ones in the plain ASCII set, except the following "
                    "ones: control characters, whitespace, &, ?, / and #.",
        max_length=256,
        min_length=1,
        regex="^((?![?&#/*])[\x00-\x7F])*$" # Make it FIWARE-Safe
    )
    type: Optional[DataTypes] = Field(
        title="metadata type",
        description="a metadata type, describing the NGSI value type of the "
                    "metadata value Allowed characters "
                    "are the ones in the plain ASCII set, except the following "
                    "ones: control characters, whitespace, &, ?, / and #.",
        max_length=256,
        min_length=1,
        regex="^((?![?&#/\*])[\x00-\x7F])*$" # Make it FIWARE-Safe
    )
    value: Optional[DataTypes] = Field(
        title="metadata value",
        description="a metadata value containing the actual metadata"
    )

class BaseContextAttribute(BaseModel):
    type: DataTypes = Field(
        default=DataTypes.TEXT,
        description="The attribute type represents the NGSI value type of the "
                    "attribute value. Note that FIWARE NGSI has its own type "
                    "system for attribute values, so NGSI value types are not "
                    "the same as JSON types. Allowed characters "
                    "are the ones in the plain ASCII set, except the following "
                    "ones: control characters, whitespace, &, ?, / and #.",
        max_length = 256,
        min_length = 1,
        regex = "^((?![?&#/])[\x00-\x7F])*$", # Make it FIWARE-Safe
    )
    value: Union[float, int, bool, str] = Field(
        title="Attribute value",
        description="the actual data"
    )
    metadata: Optional[ContextMetadata] = Field(
        title="Metadata",
        description="optional metadata describing properties of the attribute "
                    "value like e.g. accuracy, provider, or a timestamp")

    @validator('value')
    def validate_value_type(cls, v, values):
        type_ = values['type']
        if type_ == DataTypes.BOOLEAN:
            return bool(v)
        elif type_ == DataTypes.NUMBER:
            return float(v)
        else:
            return str(v)

class ContextAttribute(BaseContextAttribute):
    """
    Context attributes are properties of context entities. For example, the
    current speed of a car could be modeled as attribute current_speed of entity
    car-104.

    In the NGSI data model, attributes have an attribute name, an attribute type
    an attribute value and metadata.
    """
    name: str = Field(
        titel="Attribute name",
        description="The attribute name describes what kind of property the "
                    "attribute value represents of the entity, for example "
                    "current_speed. Allowed characters "
                    "are the ones in the plain ASCII set, except the following "
                    "ones: control characters, whitespace, &, ?, / and #.",
        max_length = 256,
        min_length = 1,
        regex = "(^((?![?&#/])[\x00-\x7F])*$)(?!(id|type|geo:distance|\*))",
        # Make it FIWARE-Safe
    )


class ContextEntity(BaseModel):
    """
    Context entities, or simply entities, are the center of gravity in the
    FIWARE NGSI information model. An entity represents a thing, i.e., any
    physical or logical object (e.g., a sensor, a person, a room, an issue in
    a ticketing system, etc.). Each entity has an entity id.
    Furthermore, the type system of FIWARE NGSI enables entities to have an
    entity type. Entity types are semantic types; they are intended to describe
    the type of thing represented by the entity. For example, a context
    entity #with id sensor-365 could have the type temperatureSensor.

    Each entity is uniquely identified by the combination of its id and type.
    """
    id: str = Field(
        ...,
        title="Entity Id",
        description="Id of an entity in an NGSI context broker. "
                    "Allowed characters are the ones in the plain ASCII set, "
                    "except the following ones: control characters, "
                    "whitespace, &, ?, / and #.",
        example='Bcn-Welt',
        max_length=256,
        min_length=1,
        regex="^((?![?&#/])[\x00-\x7F])*$", # Make it FIWARE-Safe
    )
    type: str = Field(
        ...,
        title="Enity Type",
        description="Id of an entity in an NGSI context broker. "
                    "Allowed characters are the ones in the plain ASCII set, "
                    "except the following ones: control characters, "
                    "whitespace, &, ?, / and #.",
        example="Room",
        max_length=256,
        min_length=1,
        regex="^((?![?&#/])[\x00-\x7F])*$", # Make it FIWARE-Safe
    )

    def __init__(self,
                 id: str,
                 type: str,
                 **data):
        data.update(self._validate_properties(data)) # There currently no
        # validation for extra fields
        super().__init__(id=id, type=type, **data)

    class Config(BaseConfig):
        extra = 'allow'
        validate_all = True
        validate_assignment = True

    def _validate_properties(cls, data: Dict):
        attrs = {key: BaseContextAttribute.parse_obj(attr) for key, attr in \
                data.items() if key not in ContextEntity.__fields__}
        return attrs

    def get_properties(self) -> List[ContextAttribute]:
        return [ContextAttribute(name=key, **value) for key, value in
                self.dict().items() if key not in
                ContextEntity.__fields__ and
                value.get('type') is not DataTypes.RELATIONSHIP]

    def get_relationships(self):
        return [ContextAttribute(name=key, **value) for key, value in
                self.dict().items() if key not in
                ContextEntity.__fields__ and
                value.get('type') == DataTypes.RELATIONSHIP]


def username_alphanumeric(cls, v):
    #assert v.value.isalnum(), 'must be numeric'
    return v


def create_context_entity_model(name: str = None, data: Dict = None):
    properties = {key: (BaseContextAttribute, ...) for key in data.keys() if
                  key not in ContextEntity.__fields__}
    validators = {f'validate_test': validator('temperature')(
        username_alphanumeric)}
    EntityModel = create_model(
        __model_name=name or 'GeneratedContextEntity',
        __base__=ContextEntity,
        __validators__=validators,
        **properties
    )
    return EntityModel


class Notification(BaseModel):
    subscriptionId: str = Field(
        description="Id of the subscription the notification comes from"
    )
    data: ContextEntity = Field(
        description="Context data entity"
    )















#class Relationship:
#    """
#    Class implements the concept of FIWARE Entity Relationships.
#    """
#    def __init__(self, ref_object: Entity, subject: Entity, predicate: str =
        #    None):
#        """
#        :param ref_object:  The parent / object of the relationship
#        :param subject: The child / subject of the relationship
#        :param predicate: currently not supported -> describes the
        #        relationship between object and subject
#        """
#        self.object = ref_object
#        self.subject = subject
#        self.predicate = predicate
#        self.add_ref()
#
#    def add_ref(self):
#        """
#        Function updates the subject Attribute with the relationship attribute
#        :return:
#        """
#        ref_attr = json.loads(self.get_ref())
#        self.subject.add_attribute(ref_attr)
#
#    def get_ref(self):
#        """
#        Function creates the NGSI Ref schema in a ref_dict, needed for the
        #        subject
#        :return: ref_dict
#        """
#        ref_type = self.object.type
#        ref_key = "ref" + str(ref_type)
#        ref_dict = dict()
#        ref_dict[ref_key] = {"type": "Relationship",
#                             "value": self.object.id}
#
#        return json.dumps(ref_dict)
#
#    def get_json(self):
#        """
#        Function returns a JSON to describe the Relationship,
#        which then can be pushed to orion
#        :return: whole_dict
#        """
#        temp_dict = dict()
#        temp_dict["id"] = self.subject.id
#        temp_dict["type"] = self.subject.type
#        ref_dict = json.loads(self.get_ref())
#        whole_dict = {**temp_dict, **ref_dict}
#        return json.dumps(whole_dict)
#
#
