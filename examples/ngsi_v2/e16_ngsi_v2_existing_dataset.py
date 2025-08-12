"""
This example shows how to upload an existing dataset to a FIWARE-based platform. For demonstration purposes, we
consider a simulation dataset in CSV format that contains sensor and actuator data. This dataset need to be provisioned
to the platform for further usage.

In this example, we demonstrate with a sensor and an actuator: TemperatureSensor and CoolingCoil.
"""

from typing import Optional, List
import pandas as pd
from pydantic import BaseModel
from filip.models.ngsi_v2.context import ContextEntityKeyValues
from filip.config import settings
from filip.clients.ngsi_v2 import ContextBrokerClient
from filip.models.base import FiwareHeader

SENSOR_DATA_FILE = "./e16_ngsi_v2_existing_dataset/sensor_data_1d.csv"
ACTUATOR_DATA_FILE = "./e16_ngsi_v2_existing_dataset/actuator_data_1d.csv"


class TemperatureSensor(BaseModel):
    temperature: Optional[float] = 0
    brand: Optional[str] = None
    hasLocation: str = None


class TemperatureSensorFiware(TemperatureSensor, ContextEntityKeyValues):
    type: str = "TemperatureSensor"


class CoolingCoil(BaseModel):
    # temperatureSetpoint: Optional[float] = 0
    brand: Optional[str] = None
    hasLocation: Optional[str] = None
    fanSpeed: Optional[float] = 0


class CoolingCoilFiware(CoolingCoil, ContextEntityKeyValues):
    type: str = "CoolingCoil"


def initialize_entities(cbc: ContextBrokerClient):
    """
    Create fiware entities based on the data model V2.
    """
    entities: List[ContextEntityKeyValues] = []

    # Temperature Sensor
    temperature_sensor = TemperatureSensorFiware(
        id="TemperatureSensor:001", brand="BrandX", hasLocation="Room:001"
    )
    entities.append(temperature_sensor)

    # Cooling Coil
    cooling_coil = CoolingCoilFiware(
        id="CoolingCoil:001", brand="BrandY", hasLocation="Room:001"
    )
    entities.append(cooling_coil)

    # Post entities to Context Broker
    for e in entities:
        cbc.post_entity(entity=e, update=True, key_values=True)


if __name__ == "__main__":
    fiware_header = FiwareHeader.model_validate(
        {"service": settings.FIWARE_SERVICE, "service_path": "/"}
    )
    cbc = ContextBrokerClient(fiware_header=fiware_header, url=settings.CB_URL)

    # Initialize entities in the Context Broker
    initialize_entities(cbc)

    # Load existing dataset from CSV
    sensor_df = pd.read_csv(SENSOR_DATA_FILE)
    actuator_df = pd.read_csv(ACTUATOR_DATA_FILE)

    # TODO upload sensor and actuator data to QL, INCLUDING timestamps
    temperature_measurements = sensor_df["TRm_degC"]  # numeric data
    temperature_timestamps = sensor_df["simulation_time"]

    fan_speed_setpoints = actuator_df["fcuLvlSet"]  # integer data
    fan_speed_timestamps = actuator_df["simulation_time"]

    # TODO query QL to get the uploaded data
    ...

    # TODO compare the uploaded data with the original dataset, maybe plot them
    ...
