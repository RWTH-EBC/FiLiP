import logging
import time
import random
from datetime import datetime, timedelta

from filip.config import settings
from filip.models.ngsi_v2.subscriptions import Message, Subscription
from filip.models.ngsi_v2.context import ContextEntity, NamedContextAttribute
from filip.models.base import FiwareHeader
from filip.clients.ngsi_v2 import ContextBrokerClient, QuantumLeapClient
from filip.utils.cleanup import clear_all
import matplotlib.pyplot as plt

# ## Parameters
#
# To run this example you need a working Fiware v2 setup with a
# Context Broker and QuantumLeap. Here you can set the addresses:
#
# Host address of Context Broker
CB_URL = settings.CB_URL
# Host address of QuantumLeap
QL_URL = settings.QL_URL

# Here you can also change FIWARE service and service path.
# FIWARE-Service
SERVICE = 'filip'
# FIWARE-Service path
SERVICE_PATH = '/'

# Setting up logging
logging.basicConfig(
    level='INFO',
    format='%(asctime)s %(name)s %(levelname)s: %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S')
logger = logging.getLogger(__name__)


def temperature_forecast(current_temperature):
    start_time = datetime.strptime("00:00", "%H:%M")
    end_time = datetime.strptime("04:00", "%H:%M")

    # Time step of 30 minutes
    time_step = timedelta(minutes=30)

    # Loop over time
    T = current_temperature
    current_time = start_time

    # Loop over time
    value = {}
    while current_time <= end_time:
        # Convert hours and minutes to a numerical value for t (in hours, e.g., 1.5 for 01:30)
        t = current_time.hour + current_time.minute / 60.0

        # Calculate T
        T += t ** 1.01
        value[current_time.strftime("%H:%M")] = T
        current_time += time_step
    return value


if __name__ == "__main__":
    fiware_header = FiwareHeader(service=SERVICE, service_path=SERVICE_PATH)

    # clear all existing data
    clear_all(fiware_header=fiware_header, cb_url=CB_URL, ql_url=QL_URL)

    ql_client = QuantumLeapClient(url=QL_URL, fiware_header=fiware_header)

    cb_client = ContextBrokerClient(url=CB_URL, fiware_header=fiware_header)

    # create entity for weather station
    weather_station = ContextEntity(id='WeatherStation:001',
                                    type='WeatherStation')

    # add forecast attribute in the entity
    forecast = NamedContextAttribute(
        name="temperatureForecast",
        type="StructuredValue",
        # "hh:mm": temperature
        value={
            "00:00": 20,
            "00:30": 20,
            "01:00": 20,
            "01:30": 20,
            "02:00": 20,
            "02:30": 20,
            "03:00": 20,
            "03:30": 20,
            "04:00": 20
        })
    weather_station.add_attributes([forecast])
    cb_client.post_entity(weather_station)

    # create timeseries notification for weather forecast
    forecast_subscription = Subscription(
        description="Forecast subscription",
        subject={
            "entities": [
                {
                    "id": weather_station.id,
                }
            ]
        },
        notification={
            "http": {
                "url": "http://quantumleap:8668/v2/notify"
            },
            "metadata": [
                "dateModified",
                "TimeInstant",
                "timestamp"
            ]
        },
        throttling=0
    )
    cb_client.post_subscription(forecast_subscription)

    # update forecast
    for i in range(10):
        time.sleep(1)
        # weather_station.temperatureForecast.value = forecast
        forecast.value = temperature_forecast(forecast.value["00:30"])
        # weather_station.update_attribute(forecast)
        cb_client.update_attribute_value(
            entity_id=weather_station.id,
            attr_name=forecast.name,
            value=forecast.value
        )

    # check forecast from QuantumLeap
    query = ql_client.get_entity_by_id(entity_id=weather_station.id)

    # plot the forecast
    values = query.attributes[0].values
    index = query.index
    plot_time = datetime.strptime("00:00", "%H:%M")
    # get current year , month and day
    current_date = datetime.now().date()
    plot_time = plot_time.replace(
        year=current_date.year,
        month=current_date.month,
        day=current_date.day)

    plot_time_delta = timedelta(minutes=30)
    for i, _ in enumerate(index[:]):
        index[i] = plot_time
        plot_time += plot_time_delta

    forecast_time_labels = list(values[0].keys())

    import matplotlib
    matplotlib.use('Agg')  # GUI-based backend

    # Plot each forecast
    plt.figure(figsize=(12, 6))
    for i, forecast in enumerate(values):
        forecast_values = [forecast[time] for time in forecast_time_labels]
        time_axis = [
            index[i] + timedelta(hours=int(time.split(":")[0]),
                                 minutes=int(time.split(":")[1]))
            for time in forecast_time_labels
        ]
        plt.plot(time_axis, forecast_values,
                 label=index[i].strftime("%Y-%m-%d %H:%M:%S"))

    # Customize the plot
    plt.title("Historical Forecasts at Different Time Points")
    plt.xlabel("Time (Forecast Period)")
    plt.ylabel("Forecast Value")
    plt.xticks(rotation=45)
    plt.legend(title="Forecast Time")
    plt.grid(True)
    plt.tight_layout()

    # Show the plot
    # plt.savefig("forecast.png")
    plt.show()

