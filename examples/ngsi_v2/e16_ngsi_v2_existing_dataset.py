"""
This example shows how to upload an existing dataset to a FIWARE-based platform. For demonstration purposes, we
consider a simulation dataset in CSV format that contains sensor and actuator data. This dataset need to be provisioned
to the platform for further usage.

In this example, we demonstrate with a sensor and an actuator: TemperatureSensor and CoolingCoil.
"""

import time
from typing import Optional, List
import pandas as pd
from pydantic import BaseModel
from filip.models.ngsi_v2.context import ContextEntityKeyValues, ContextEntity
from filip.config import settings
from filip.clients.ngsi_v2 import QuantumLeapClient
from filip.models.base import FiwareHeader
from filip.models.ngsi_v2.subscriptions import Message
from filip.utils.cleanup import clear_quantumleap

import matplotlib.pyplot as plt

SENSOR_DATA_FILE = "./e16_ngsi_v2_existing_dataset/sensor_data_1d.csv"
ACTUATOR_DATA_FILE = "./e16_ngsi_v2_existing_dataset/actuator_data_1d.csv"

FIWARE_SERVICEPATH = "/test_dataset"


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


def create_entities():
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
    return entities


def create_notifications(values: pd.Series, timestamps: pd.Series, entity) -> list:
    """
    Create NGSIv2 Message objects for QuantumLeap from single-column pd.Series of values and timestamps.

    Args:
        id: Entity ID
        entity_type: Entity type (e.g., "TemperatureSensor")
        values: pd.Series of measurements
        timestamps: pd.Series of timestamps

    Returns:
        List of Message objects ready for QuantumLeap
    """
    if len(values) != len(timestamps):
        raise ValueError(
            f"Length mismatch: {len(values)} values vs {len(timestamps)} timestamps"
        )

    messages_temp = []

    for val, ts in zip(values, timestamps):
        # Ensure timestamp is ISO string
        if not isinstance(ts, str):
            ts = pd.to_datetime(ts, unit="s").isoformat()

        entity_data = {}

        attributes_dict = {"fcuLvlSet": "fanSpeed", "TRm_degC": "temperature"}

        # Use Series names as attribute keys
        entity_data[attributes_dict[str(values.name)]] = {
            "type": "Number",
            "value": float(val),
        }
        entity_data["timestamp"] = {"type": "DateTime", "value": ts}

        # Create ContextEntity
        entity = ContextEntity(id=entity.id, type=entity.type, **entity_data)

        # Wrap in Message
        message = Message(data=[entity], subscriptionId="test_dataset")
        messages_temp.append(message)

    return messages_temp


def plot_vs_time(timestamps, values, title, ylabel, marker="o"):
    """
    Plot a series of values vs simulation time (seconds relative to first timestamp).

    Parameters:
        timestamps : list or array-like
            Raw timestamps in seconds (numeric).
        values : list or array-like
            Values corresponding to timestamps.
        title : str
            Plot title.
        ylabel : str
            Label for y-axis.
        marker : str, optional
            Marker style for the plot (default: "o").
    """

    ts = pd.Series(timestamps)

    # Handle datetime
    if pd.api.types.is_datetime64_any_dtype(ts):
        simulation_time_sec = (ts - ts.iloc[0]).dt.total_seconds()
    else:
        simulation_time_sec = ts - ts.iloc[0]

    # Plot
    plt.plot(simulation_time_sec, values, marker=marker)
    plt.title(title)
    plt.xlabel("Simulation Time (s)")
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.show()


def send_notifications(client: "QuantumLeapClient", notifications: list["Message"]):
    """
    Send a list of notifications to a QuantumLeap client.

    Iterates through each message in the notifications list and posts it
    using the provided QuantumLeap client.

    Parameters:
        client (QuantumLeapClient): An instance of the QuantumLeap client used to send notifications.
        notifications (list[Message]): A list of Message objects to be sent.

    Returns:
        None
    """
    for message in notifications:
        client.post_notification(message)


def prepare_dataframe(df, timestamp_col="timestamp", value_col="temperature"):
    """
    Prepare a DataFrame for plotting or analysis:
    - Flattens MultiIndex columns if needed
    - Converts timestamp column to datetime
    - Converts value column to numeric

    Parameters:
        df : pd.DataFrame
            Input DataFrame
        timestamp_col : str
            Name of the timestamp column
        value_col : str
            Name of the numeric value column

    Returns:
        pd.DataFrame : cleaned DataFrame
    """
    df = df.copy()  # avoid modifying original

    # Flatten MultiIndex if needed
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[-1] for col in df.columns]

    # Convert timestamp column to datetime with UTC
    df[timestamp_col] = pd.to_datetime(df[timestamp_col], utc=True)

    # Ensure value column is numeric
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")

    return df


if __name__ == "__main__":

    fiware_header = FiwareHeader.model_validate(
        {"service": settings.FIWARE_SERVICE, "service_path": FIWARE_SERVICEPATH}
    )

    # clear existing data
    ql = QuantumLeapClient(fiware_header=fiware_header, url=settings.QL_URL)
    clear_quantumleap(ql_client=ql)

    # entities[]  0: Sensor  1: Actuator
    entities = create_entities()

    # Load existing dataset from CSV
    sensor_df = pd.read_csv(SENSOR_DATA_FILE)
    actuator_df = pd.read_csv(ACTUATOR_DATA_FILE)

    temperature_measurements = sensor_df["TRm_degC"]  # numeric data
    temperature_timestamps = sensor_df["simulation_time"]

    fan_speed_setpoints = actuator_df["fcuLvlSet"]  # integer data
    fan_speed_timestamps = actuator_df["simulation_time"]

    # Send measurements to Quantumleap
    messages = create_notifications(
        temperature_measurements, temperature_timestamps, entities[0]
    )
    send_notifications(ql, messages)
    messages = create_notifications(
        fan_speed_setpoints, fan_speed_timestamps, entities[1]
    )
    send_notifications(ql, messages)

    # wait for few seconds so data is available
    time.sleep(2)

    # query data from quantumleap
    res_temperature = ql.get_entity_values_by_id(entity_id=entities[0].id)
    res_fan_speed_setpoint = ql.get_entity_values_by_id(entity_id=entities[1].id)

    # prepare queried data for plotting
    df_temperature = prepare_dataframe(
        res_temperature.to_pandas(), "timestamp", "temperature"
    )
    df_fan_speed_setpoint = prepare_dataframe(
        res_fan_speed_setpoint.to_pandas(), "timestamp", "fanSpeed"
    )

    # plot original data
    plot_vs_time(
        temperature_timestamps,
        temperature_measurements,
        "Temperature vs Simulation Time (Original data)",
        "Temperature (°C)",
    )
    plot_vs_time(
        fan_speed_timestamps,
        fan_speed_setpoints,
        "Fan Speed Setpoint vs Simulation Time (Original data)",
        "Fan Speed Setpoint",
    )

    # plot quantumleap data
    plot_vs_time(
        df_temperature["timestamp"],
        df_temperature["temperature"],
        "Temperature vs Simulation Time (QuantumLeap data)",
        "Temperature (°C)",
    )
    plot_vs_time(
        df_fan_speed_setpoint["timestamp"],
        df_fan_speed_setpoint["fanSpeed"],
        "Fan Speed Setpoint vs Simulation Time (QuantumLeap data)",
        "Fan Speed Setpoint",
    )
