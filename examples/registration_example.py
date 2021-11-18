"""
created Sep 21, 2021

@author Thomas Storek

Steps :
1. Create a context provider
2. Create an context entity retrieving information from a context provider


"""
# import
from filip.clients.ngsi_v2.cb import ContextBrokerClient
from filip.models.base import FiwareHeader
from filip.models.ngsi_v2.base import NamedMetadata
from filip.models.ngsi_v2.context import \
    ContextAttribute, \
    ContextEntity
from filip.models.ngsi_v2.units import Unit
from filip.models.ngsi_v2.registrations import Http, Provider, Registration

# Create a building with a weather station as context provider
# We start from the meta data here. The other way round is also possible but
# using the api of the Context Entity Model

# Create unit metadata for the temperature sensor of the weather staion
temperature_metadata = NamedMetadata(name="unit",
                                     value=Unit(name="degree Celsius").dict())
# create the temperature attribute of the weather station
temperature = ContextAttribute(type="Number",
                               value=20.5)
                               #metadata=temperature_metadata)
# create the complete model of the building with the weather station
weather_station = ContextEntity(id="urn:ngsi-ld:WeatherStation:001",
                           type="WeatherStation",
                           temperature=temperature)

# print complete weather station object
print("+"*80)
print("Building with weather station with one property from a sensor")
print("+"*80)
print(weather_station.json(indent=2))

# create additional properties of the weather station
windspeed_metadata = NamedMetadata(name="unit",
                                   type="Unit",
                                   value=Unit(name="kilometre per "
                                                          "hour").dict())
# create the temperature attribute of the weather station
windspeed = ContextAttribute(type="Number",
                             value=60)#,
                             #metadata=windspeed_metadata)
weather_station.add_attributes(attrs={"windspeed": windspeed})

# print complete model
print("+"*80)
print("Building with weather station with two properties from a sensor")
print("+"*80)
print(weather_station.json(indent=2))

building_1 = ContextEntity(id="urn:ngsi-ld:building:001",
                           type="Building")

print("+"*80)
print("Building without own properties")
print("+"*80)
print(building_1.json(indent=2))

# create registration for the weather station as context provider
http = Http(url=f"http://localhost:1026/v2")
provider = Provider(http=http)
registration = Registration.parse_obj(
    {
        "description": "Weather Conditions",
        "dataProvided": {
            "entities": [
                {
                    "idPattern": ".*",
                    "type": "Building",
                }
            ],
            "attrs": ["temperature", "windspeed"]
        },
        "provider": provider.dict()
    })
print("+"*80)
print("Registration that makes the first building a context "
      "provider for the second building")
print("+"*80)
print(registration.json(indent=2))

fiware_header = FiwareHeader(service="filip",
                             service_path="/testing")
print(fiware_header.json(by_alias=True, indent=2))
client = ContextBrokerClient(url="http://134.130.166.184:1026",
                             fiware_header=fiware_header)
client.post_entity(entity=weather_station)
client.post_entity(entity=building_1)
registration_id = client.post_registration(registration=registration)
print(registration_id)
registration =client.get_registration(registration_id=registration_id)
print(registration.json(indent=2))

weather_station = client.get_entity(entity_id=weather_station.id,
                               entity_type=weather_station.type)
print(weather_station.json(indent=2))
building_1 = client.get_entity(entity_id=building_1.id,
                               entity_type=building_1.type)
print(building_1.json(indent=2))

registration =client.get_registration(registration_id=registration_id)
print(80*"+" + "\n" + registration.json(indent=2))


from filip.models.ngsi_v2.context import EntityPattern, Query
entity = EntityPattern(idPattern=".*", type="Building")
query = Query(entities=[entity])

print(query.json(indent=2))

res = client.query(query=query)
for entity in res:
    print(entity.json(indent=2))


client.delete_entity(entity_id=weather_station.id,
                     entity_type=weather_station.type)
client.delete_entity(entity_id=building_1.id,
                     entity_type=building_1.type)
client.delete_registration(registration_id)
