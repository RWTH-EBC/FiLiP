# N5GEH Cluster Tutorials

## Introduction

The N5GEH Cluster is a publicly available FIWARE-based IoT platform
deployment. All platform APIs are protected through authentication and
authorization, so every request must carry a valid access token. This
tutorial will guide you through the steps to access the N5GEH Cluster and
progressively explore its features: from understanding basic MQTT
communication to deploying your own IoT application.

## Tutorial Overview

The tutorial consists of three parts that build on each other. It is
recommended to complete them in the given order.

| Tutorial | Focus | What you will do |
| -------- | ----- | ---------------- |
| [Tutorial 1: MQTT Basics](t1_mqtt_basics/README.md) | Communication via MQTT | Create a virtual weather station that publishes simulated ambient temperature to an MQTT broker and receives it again with a subscriber. |
| [Tutorial 2: Provisioning Sensors](t2_provision_sensor/README.md) | The FIWARE data pipeline | Provision two virtual sensors, stream their data via MQTT to the IoT Agent and store the history in QuantumLeap. |
| [Tutorial 3: Deploying a Controller](t3_deploy_controller/README.md) | A closed control loop | Add a virtual heater actuator and a hysteresis controller that keeps the zone temperature within a given band. |

## FIWARE-Service and Multi-Tenancy

The N5GEH Cluster hosts a single instance of each platform component but
serves many independent users. Multi-tenancy is the feature that allows
multiple **independent** sub-platforms (tenants) to operate within a single
platform instance. Each tenant maintains complete logical isolation with its
own data storage, user management, and access control policies. This design
enables:

* **Data Isolation:** Each tenant's context data and subscriptions are
  isolated from other tenants. Users from one tenant cannot access data
  belonging to another tenant.
* **Independent User Management:** Each tenant maintains its own set of users
  and roles. User credentials and permissions are scoped to a specific tenant
  only.
* **Isolated Configuration:** Tenant-specific authentication and
  authorization policies are configured independently without affecting other
  tenants.

The tenant identification mechanism is enforced through the `Fiware-Service`
header, which must be specified in every API request. This header serves as
the primary tenant selector and is validated against the user's tenant
associations before processing any request. The `Fiware-ServicePath` header
additionally scopes the data within a tenant and is set to `/` in these
tutorials.

Test FIWARE services are available as `ebcdev1` to `ebcdev5`. This tutorial
series uses `ebcdev1`, which is defined as `SERVICE` in `init_clients.py`.

## Prerequisites

Since all platform components (MQTT broker, Orion Context Broker, IoT Agent,
QuantumLeap, etc.) are already deployed on the cluster, you only need to
correctly authenticate yourself:

- **Credentials:** The credentials of the test FIWARE services are provided
  in Passbolt. Add the correct credentials for your FIWARE service in `credential` file.
- **Client id convention:** The client id is derived from the FIWARE service
  name, e.g. `ebcdev1-admin` for the service `ebcdev1`. It is automatically
  composed as `f"{SERVICE}-admin"` in `init_clients.py`.
- **Access rights:** The access tokens are scoped to the following
  operations: `read` for GET requests, `write` for PUT, PATCH and POST
  requests, and `admin` for DELETE requests.
- **Python environment:** Install the required dependencies, e.g. `filip`,
  `paho-mqtt` and `matplotlib`.

To verify that your credentials and configuration are correct, run

```bash
python init_clients.py
```

This checks the version endpoints of the Context Broker, the IoT Agent and
QuantumLeap and prints them on success.
