"""
# This example shows a workflow, how you can define or reuse use case specific data
# models and ensure FIWARE compatibility by merging these models with existing data
# model in FiLiP. The merged models can be used for interaction with FIWARE platform
# and in other information processing systems to establish interoperability.

# In short: this workflow shows you a way to keep use case model simple and
# reusable while ensuring the compatability with FIWARE NGSI-V2 standards
"""
from pydantic import ConfigDict, BaseModel
from pydantic.fields import Field, FieldInfo
from filip.models import FiwareHeader
from filip.models.ngsi_v2.context import ContextEntityKeyValues
from filip.clients.ngsi_v2.cb import ContextBrokerClient
from pprint import pprint

# Host address of Context Broker
CB_URL = "http://localhost:1026"

# You can here also change the used Fiware service
# FIWARE-Service
SERVICE = 'filip'
# FIWARE-Servicepath
SERVICE_PATH = '/'
fiware_header = FiwareHeader(service=SERVICE,
                             service_path=SERVICE_PATH)


# Reuse existing data model from the internet
class PostalAddress(BaseModel):
    """
    https://schema.org/PostalAddress
    """

    model_config = ConfigDict(populate_by_name=True, coerce_numbers_to_str=True)

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


# It is assumed that this kind of models exists in use case, which is simple and use case
# specific. It describes basically, how does the data look like in the specific use case.
class WeatherStation(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True, extra="ignore")
    temperature: float = Field(default=20.0)
    humidity: float = Field(default=50.0)
    pressure: float = Field(default=1.0)
    address: PostalAddress


# Merge the use case model with the FIWARE simplified data model to ensure FIWARE
# compatibility.
class WeatherStationFIWARE(WeatherStation, ContextEntityKeyValues):
    # add default for type if not explicitly set
    type: str = FieldInfo.merge_field_infos(
        # First position is the field info of the parent class
        ContextEntityKeyValues.model_fields["type"],
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


if __name__ == "__main__":
    # Now we can export both the use case model and the FIWARE specific
    # models to json-schema files and share it with other stakeholders
    # that need the data.
    use_case_model = WeatherStation.model_json_schema()
    pprint(use_case_model)

    fiware_specific_model = WeatherStationFIWARE.model_json_schema()
    pprint(fiware_specific_model)

    # Workflow to utilize these data models.

    # 0. Initial client
    cb_client = ContextBrokerClient(url=CB_URL,
                                    fiware_header=fiware_header)

    # 1. Crate data
    weather_station = WeatherStationFIWARE(
        id="myWeatherStation",
        type="WeatherStation",
        temperature=20,
        address={
            "address_country": "Germany",
            "street_address": "Mathieustr. 10",
            "postal_code": 52072,
        },
    )
    cb_client.post_entity(entity=weather_station, key_values=True,
                          update=True)

    # 2. Update data
    weather_station.temperature = 30  # represent use case algorithm
    cb_client.update_entity_key_values(entity=weather_station)

    # 3. Query and validate data
    # represent querying data by data users
    weather_station_data = cb_client.get_entity(entity_id="myWeatherStation",
                                                response_format="keyValues")
    ## validate with general model
    weather_station_2_general = WeatherStation.model_validate(
        weather_station_data.model_dump()
    )
    ## validate with fiware specific model
    weather_station_2_fiware = WeatherStationFIWARE.model_validate(
        weather_station_data.model_dump()
    )

    # 4. Use data for different purposes
    #  for use case specific usage
    print("Data complied with general model can be forwarded to other platform/system:\n"
          f"{weather_station_2_general.model_dump_json(indent=2)}")
    print(f"For example, address still comply with existing model:\n"
          f"{weather_station_2_general.address.model_dump_json(indent=2)}\n")

    #  for fiware specific usage
    print("For usage within FIWARE system, id and type is helpful, e.g. for creating"
          "notification for entity:\n"
          f"{weather_station_2_fiware.model_dump_json(indent=2, include={'id', 'type'})}\n")
