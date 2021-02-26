from aenum import Enum
from typing import Any, List, Dict, Union, Optional
from pydantic import BaseModel, Field, validator, ValidationError, \
    root_validator, create_model
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
                    "accurate a given attribute value is"
    )
    type: Optional[DataTypes] = Field(
        title="metadata type",
        description="a metadata type, describing the NGSI value type of the "
                    "metadata value"
    )
    value: Optional[DataTypes] = Field(
        title="metadata value",
        description="a metadata value containing the actual metadata"
    )


class ContextAttribute(BaseModel):
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
                    "current_speed."
    )
    type: DataTypes = Field(
        default=DataTypes.TEXT,
        description="The attribute type represents the NGSI value type of the "
                    "attribute value. Note that FIWARE NGSI has its own type "
                    "system for attribute values, so NGSI value types are not "
                    "the same as JSON types."
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




class BaseContextEntity(BaseModel):
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
        description='Id of an entity in a NGSI context broker',
        example='Bcn-Welt',
        regex="^[\w\:\-\_]*$" # Make it FIWARE-Safe
    )
    type: str = Field(
        ...,
        description="",
        example="Room",
        regex="^[\w\:\-\_]*$" # Make it FIWARE-Safe
    )

    class Config:
        extra = 'allow'
        #validate_all = True
        #validate_assignment = True

def create_context_entity_model(name:str, data: Dict):
    properties = []
    for key in data.keys():
        if key not in BaseContextEntity.__fields__.keys():
            pass
    EntityModel = create_model(
        __model_name='MyModel',
        __base__=BaseContextEntity,
        **fields
    )
    return EntityModel








if __name__ == '__main__':
    attr = {"type": "Number", "value": 5}
    attr2 = ContextAttribute(name="myAttr2", type="Number", value=10)
    entity = BaseContextEntity(id="myRoom",
                                type='bldg:room',
                                properties=[attr2],
                                T1=attr)
    print(entity.json(indent=2))
    fields={'foo': (str, ...)}

    entity2 = EntityModel(id="ds", type="sad", foo='test')

    print(entity2.json(indent=2))



