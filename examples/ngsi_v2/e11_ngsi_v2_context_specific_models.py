"""
# This example shows how you can build useful context-specific data model
# classes from context entity data and export them to json-schema files.
# This can be useful if you want share models for specific context entities.
# Or use the context-entity models for Context Provider implementations in,
# e.g., FastAPI or Django.
#
# E.g. the Smart Data Models provide their models in such format.
# https://www.fiware.org/developers/smart-data-models/

# In short: This functionality can be used whenever context entities
# of a similar type are required. Using default values and type hints makes
# duplication of code unnecessary and allows for a more consistent
# entities and systems.
"""
import json
from pprint import pprint
from typing import Literal

from pydantic import ConfigDict, BaseModel

# ## Import packages
from pydantic.fields import FieldInfo, Field

from filip.models.ngsi_v2.context import ContextEntity, ContextAttribute


# Define a context specific attribute model, e.g. an attribute that holds
# the postal address of location.


# First, define the model for the address structure itself. Here, we use the
# schema.org definition for a postal address.
class AddressModel(BaseModel):
    """
    https://schema.org/PostalAddress
    """

    model_config = ConfigDict(populate_by_name=True)

    address_country: str = Field(
        alias="addressCountry",
        description="County code according to ISO 3166-1-alpha-2",
    )
    street_address: str = Field(
        alias="streetAddress",
        description="The street address. For example, 1600 Amphitheatre Pkwy.",
    )
    address_region: str = Field(
        alias="addressRegion",
        default=None,
    )
    address_locality: str = Field(
        alias="addressLocality",
        default=None,
        description="The locality in which the street address is, and which is "
        "in the region. For example, Mountain View.",
    )
    postal_code: str = Field(
        alias="postalCode",
        default=None,
        description="The postal code. For example, 94043.",
    )


# Now, define a context specific attribute for the address. Here, we use the
# previously defined address model as type for the value.
# Furthermore, we set the default type of the attribute to "PostalAddress"
# to give the user a type-hint. Your may also allow multiple types during
# creation.
class AddressAttribute(ContextAttribute):
    """
    Context attribute for address
    """

    def __init__(self, type: str = None, **data):
        if type is None and self.model_fields["type"].default:
            type = self.model_fields["type"].default
        super().__init__(type=type, **data)

    # add default for type if not explicitly set
    type: Literal["PostalAddress"] = FieldInfo.merge_field_infos(
        # First position is the field info of the parent class
        ContextAttribute.model_fields["type"],
        # set the default value
        default="PostalAddress",
        # overwrite the description
        description="Type of the Address",
        # freeze the field if necessary, e.g. if you want to prevent the user
        # from changing the type after creation.
        frozen=True,
        # for more options see the pydantic documentation
    )
    # add the value model. If you want to enforce the value to be set you can
    # remove the default value
    value: AddressModel = None


# Define a context specific model for a weather station
# First, inherit from the ContextEntity class, where each additional attribute
# must be of type ContextAttribute
class WeatherStation(ContextEntity):
    """
    A context specific model for a weather station
    """
    # add default for type if not explicitly set
    type: str = FieldInfo.merge_field_infos(
        # First position is the field info of the parent class
        ContextEntity.model_fields["type"],
        # set the default value
        default="CustomModels:WeatherStation",
        # overwrite the title in the json-schema if necessary
        title="Type of the Weather Station",
        # overwrite the description
        description="Type of the Weather Station",
        # validate the default value if necessary
        validate_default=True,
        # freeze the field if necessary
        frozen=True,
        # for more options see the pydantic documentation
    )
    # add model specific attributes including their type.
    temperature: ContextAttribute = ContextAttribute(type="Number")
    humidity: ContextAttribute = ContextAttribute(type="Number")
    pressure: ContextAttribute = ContextAttribute(type="Number")
    # add the customized address attribute with an empty value
    # how strict validation will be performed depends on the used pydantic
    # address model. Hence, the user can define the validation rules for it and
    # ship them with the schema file.
    address: AddressAttribute = AddressAttribute()


if __name__ == "__main__":
    # Now we can create the weather station model and export it to a
    # json-schema file without explicitly defining the entity-type.
    # Furthermore, we can use the model to create a new weather station entity
    weather_station = WeatherStation(
        id="myWeatherStation",
        type="brick:WeatherStation",
        temperature={"type": "Number",
                     "value": 25},
        address={"type": "PostalAddress",
                 "value": {
                     # required attributes
                     "address_country": "Germany",
                     "street_address": "Mathieustr. 10",
                     # optional attributes
                     "postal_code": "52072",
                 }}
    )
    print(weather_station.model_dump_json(indent=2))

    # ## Export the model to a json-schema file. The schema now contains all
    # added information about the customized model. Please note that the
    # field `type` is no-longer a required field, as it is set to a default
    # value.
    pprint(weather_station.model_json_schema())

    # To compare to the version without the custom model, see the output of
    # the following code which would still require the user to define the type:
    weather_station_reference = ContextEntity.model_validate(weather_station.model_dump())
    pprint(weather_station_reference.model_json_schema())
