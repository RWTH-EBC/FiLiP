"""
Usually the live data is stored in Context Broker and the historical data in the time
series database. However, there is a specific use case, where the live data itself is a
time series, i.e. the forecast data.

This is not a trivial task, because by default the historical forecasts will be saved
as objects in the time series database, complicating the request and the visualization
in dashboard.

In this example, we will demonstrate the best practice to save the forecast data in
Context Broker and in the time series database.
"""

import logging
import time
from datetime import datetime, timedelta
from filip.config import settings
from filip.models.ngsi_v2.subscriptions import Message, Subscription
from filip.models.ngsi_v2.context import ContextEntity, NamedContextAttribute
from filip.models.base import FiwareHeader
from filip.clients.ngsi_v2 import ContextBrokerClient, QuantumLeapClient
from filip.utils.cleanup import clear_all

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
SERVICE = 'filip_e15'
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
    temperature = NamedContextAttribute(
        name="temperature",
        type="Number",
        value=20
    )
    weather_station.add_attributes([temperature, forecast])

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
        temperature.value = forecast.value["00:00"]
        forecast.value = temperature_forecast(forecast.value["00:30"])
        weather_station.update_attribute([temperature, forecast])
        cb_client.update_entity(weather_station)

    # check forecast from QuantumLeap
    query = ql_client.get_entity_by_id(entity_id=weather_station.id)
    forecast_history = ql_client.get_entity_attr_values_by_id(
        entity_id=weather_station.id,
        attr_name=forecast.name)
    temperature_history = ql_client.get_entity_attr_values_by_id(
        entity_id=weather_station.id,
        attr_name=temperature.name)

    # Modify the time index
    index = forecast_history.index
    # index = query.index
    plot_time = datetime.strptime("00:00", "%H:%M")
    # get current year , month and day
    current_date = datetime.now().date()
    plot_time = plot_time.replace(
        year=current_date.year,
        month=current_date.month,
        day=current_date.day)
    plot_time_delta = timedelta(minutes=30)
    for i, _ in enumerate(index[:]):
        forecast_history.index[i] = plot_time
        temperature_history.index[i] = plot_time
        plot_time += plot_time_delta

    # Plot the history with plotly
    import plotly.graph_objects as go
    from datetime import timedelta

    # Create a Plotly figure
    fig = go.Figure()

    # Add historical forecast to the plot
    forecast_time_labels = list(forecast_history.attributes[0].values[0].keys())
    for i, forecast in enumerate(forecast_history.attributes[0].values):
        forecast_values = [forecast[time] for time in forecast_time_labels]
        time_axis = [
            forecast_history.index[i] + timedelta(hours=int(time.split(":")[0]),
                                                  minutes=int(time.split(":")[1]))
            for time in forecast_time_labels
        ]
        fig.add_trace(go.Scatter(
            x=time_axis,
            y=forecast_values,
            mode='lines',
            name="Forecast "+index[i].strftime("%Y-%m-%d %H:%M:%S")
        ))

    # Add temperature history to the plot
    # for i, temperature in enumerate(temperature_history.attributes[0].values):
    temperature_values = temperature_history.attributes[0].values
    fig.add_trace(go.Scatter(
        x=temperature_history.index,
        y=temperature_values,
        mode='lines',
        line=dict(width=4),  # Make the temperature lines thicker
        name=f"Temperature History",
    ))

    # Customize the layout
    fig.update_layout(
        title="Historical Data",
        xaxis_title="Time",
        yaxis_title="Value",
        xaxis=dict(
            tickangle=45
        ),
        template="plotly_white"
    )

    # Add gridlines
    fig.update_xaxes(showgrid=True)
    fig.update_yaxes(showgrid=True)

    # Show the plot
    fig.show()

    # An example to query data directly from CrateDB, for example via Grafana
    query = f"""SELECT entity_id, entity_type, time_index, 
                                           temperatureforecast['00:00'], 
                                           temperatureforecast['00:30'], 
                                           temperatureforecast['01:00'], 
                                           temperatureforecast['01:30'], 
                                           temperatureforecast['02:00'], 
                                           temperatureforecast['02:30'], 
                                           temperatureforecast['03:00'], 
                                           temperatureforecast['03:30'],
                                           temperatureforecast['04:00']
                FROM "etweatherstation"
                LIMIT 100;
    """

