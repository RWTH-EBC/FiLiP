"""
# Example describing how registrations works
#
# Steps :
# 1. Create a context provider
# 2. Create a context entity retrieving information from a context provider
"""

# ## Import packages
import logging
from filip.clients.ngsi_v2.cb import ContextBrokerClient
from filip.models.base import FiwareHeader
from filip.models.ngsi_v2.base import NamedMetadata
from filip.models.ngsi_v2.context import ContextAttribute, ContextEntity
from filip.models.ngsi_v2.units import Unit
from filip.models.ngsi_v2.registrations import Http, Provider, Registration
from filip.config import settings

# ## Parameters
#
# To run this example you need a working Fiware v2 setup with a context-broker
# You can set the address:
#
# Host address of Context Broker
CB_URL = settings.CB_URL

# You can also change the used Fiware service
# FIWARE-Service
SERVICE = "filip"
# FIWARE-Service path
SERVICE_PATH = "/example"

# Setting up logging
logging.basicConfig(
    level="INFO",
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # # 1 Creating models
    #
    # Create a building with a weather station as a context provider.
    # We start by creating metadata. The other way round is also possible, but
    # you have to use the api of the Context Entity Model.

    # create unit metadata for the temperature sensor of the weather station
    temperature_metadata = NamedMetadata(
        name="unit", type="Unit", value=Unit(name="degree Celsius").model_dump()
    )
    # create the 'temperature' attribute of the weather station
    temperature = ContextAttribute(
        type="Number", value=20.5, metadata=temperature_metadata
    )
    # create the complete model of the weather station
    weather_station = ContextEntity(
        id="urn:ngsi-ld:WeatherStation:001",
        type="WeatherStation",
        temperature=temperature,
    )

    # print the complete weather station object
    print(f"{'*' * 80}\nWeather station with one attribute\n{'*' * 80}")
    print(weather_station.model_dump_json(indent=2))

    # create an additional attribute 'wind_speed' of the weather station
    wind_speed_metadata = NamedMetadata(
        name="unit", type="Unit", value=Unit(name="kilometre per " "hour").model_dump()
    )
    # create the temperature attribute of the weather station
    wind_speed = ContextAttribute(type="Number", value=60, metadata=wind_speed_metadata)
    weather_station.add_attributes(attrs={"wind_speed": wind_speed})

    # print the complete model
    print(f"{'*' * 80}\nWeather station with two attributes\n{'*' * 80}")
    print(weather_station.model_dump_json(indent=2))

    building = ContextEntity(id="urn:ngsi-ld:building:001", type="Building")

    print(f"{'*' * 80}\nBuilding without own attributes\n{'*' * 80}")
    print(building.model_dump_json(indent=2))

    # # 2 Creating registration
    #
    # create a registration for the weather station as a context provider
    http = Http(url=f"http://localhost:1026/v2")
    provider = Provider(http=http)
    registration = Registration.model_validate(
        {
            "description": "Weather Conditions",
            "dataProvided": {
                "entities": [
                    {
                        "idPattern": ".*",
                        "type": "Building",
                    }
                ],
                "attrs": ["temperature", "wind_speed"],
            },
            "provider": provider.model_dump(),
        }
    )
    print(
        f"{'*' * 80}\nRegistration that makes the weather station a context provider for the building\n{'*' * 80}"
    )
    print(registration.model_dump_json(indent=2))

    # # 3 Post created objects to Fiware
    #
    fiware_header = FiwareHeader(service=SERVICE, service_path=SERVICE_PATH)
    client = ContextBrokerClient(url=CB_URL, fiware_header=fiware_header)
    client.post_entity(entity=weather_station)
    client.post_entity(entity=building)
    registration_id = client.post_registration(registration=registration)

    # # 4 Reading objects from Fiware
    #
    #
    registration = client.get_registration(registration_id=registration_id)
    print(f"{'*' * 80}\nPosted registration to the context broker\n{'*' * 80}")
    print(registration.model_dump_json(indent=2))

    weather_station = client.get_entity(
        entity_id=weather_station.id, entity_type=weather_station.type
    )
    print(f"{'*' * 80}\nPosted weather station to the context broker\n{'*' * 80}")
    print(weather_station.model_dump_json(indent=2))

    building = client.get_entity(entity_id=building.id, entity_type=building.type)
    print(f"{'*' * 80}\nPosted building to the context broker\n{'*' * 80}")
    print(building.model_dump_json(indent=2))

    # # 5 Query Fiware
    #
    from filip.models.ngsi_v2.context import EntityPattern, Query

    entity = EntityPattern(idPattern=".*", type="Building")
    query = Query(entities=[entity])

    print(f"{'*' * 80}\nQuery with the idPattern='.*' and type='Building\n{'*' * 80}")
    print(query.model_dump_json(indent=2))

    res = client.query(query=query)
    for entity in res:
        print(entity.model_dump_json(indent=2))

    # # 6 Delete objects
    #
    client.delete_entity(entity_id=weather_station.id, entity_type=weather_station.type)
    client.delete_entity(entity_id=building.id, entity_type=building.type)
    client.delete_registration(registration_id)
