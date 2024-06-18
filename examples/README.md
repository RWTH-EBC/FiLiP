# Examples

This directory contains examples to support you how to use FiLiP to 
build smart solutions based on FIWARE.  
In order to execute the examples you need a working FIWARE instance. For more details
look into the [required prerequisites](https://github.com/RWTH-EBC/FiLiP?tab=readme-ov-file#prerequisites) of the
library.  
Each example should be executable with only small adjustments according to 
your FIWARE instance, e.g. URL settings.

The following topics are covered:

#### How to use the clients and use general settings?

- [http-clients](./basics/e01_http_clients.py) 
- [logging](./basics/e11_logging.py) 
- [settings-management](./basics/e12_settings.py)

#### How to model context and interact with Orion Context Broker?
    
- [Context Basics](./ngsi_v2/e01_ngsi_v2_context_basics.py) 
- [Context Relationships](./ngsi_v2/e02_ngsi_v2_context_relationships.py)
- [Context HTTP Subscriptions](./ngsi_v2/e03_ngsi_v2_context_subscriptions_http.py)
- [Context MQTT Subscriptions](./ngsi_v2/e04_ngsi_v2_context_subscriptions_mqtt.py)
- [Context Registrations](./ngsi_v2/e05_ngsi_v2_context_registrations.py)
- [Context Model Generation](./ngsi_v2/e06_ngsi_v2_autogenerate_context_data_models.py)

#### How to interact with IoT-Agent?

- [IoT Basics](./ngsi_v2/e07_ngsi_v2_iota_basics.py)
- [IoT Paho MQTT](./ngsi_v2/e08_ngsi_v2_iota_paho_mqtt.py)
- [IoT FiLiP MQTT](./ngsi_v2/e09_ngsi_v2_iota_filip_mqtt.py)
  (We implemented this for magic MQTT-Topic handling)

#### How to handle time series data and interact with QuantumLeap?

- [Time Series Data](./ngsi_v2/e10_ngsi_v2_quantumleap.py)
  with QuantumLeap

#### How to use ontologies for semantic system modelling?

- [Semantics](./ngsi_v2/e11_ngsi_v2_semantics)
- [Use-case specific data modeling](./ngsi_v2/e12_ngsi_v2_use_case_models.py)

