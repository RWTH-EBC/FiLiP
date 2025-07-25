![E.ON EBC RWTH Aachen University](https://raw.githubusercontent.com/RWTH-EBC/FiLiP/master/docs/logos/EBC_Logo.png)

# FiLiP

[![pylint](https://rwth-ebc.github.io/FiLiP/master/pylint/pylint.svg)](https://rwth-ebc.github.io/FiLiP/master/pylint/pylint.html)
[![Documentation](https://rwth-ebc.github.io/FiLiP/master/docs/doc.svg)](https://rwth-ebc.github.io/FiLiP/master/docs/index.html)
[![coverage](https://rwth-ebc.github.io/FiLiP/coverage/badge.svg)](https://rwth-ebc.github.io/FiLiP/coverage)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![build](https://rwth-ebc.github.io/FiLiP/master/build/build.svg)](https://rwth-ebc.github.io/FiLiP/master/build/build.svg)
[![DOI](https://joss.theoj.org/papers/10.21105/joss.06953/status.svg     )](https://doi.org/10.21105/joss.06953    )

FiLiP (Fiware Library for Python) is a python Software Development Kit (SDK) for 
accelerating the development of web services that use Fiware's Generic 
Enablers (GEs) as backend.

It is mainly based on the [Pydantic](https://pydantic-docs.helpmanual.io/) 
package which is a sophisticated library for data validation and settings 
management using python type annotations.
Pydantic enforces type hints at runtime, and provides user friendly errors 
when data is invalid.
We mainly use the Pydantic model to build our own data model structure required 
for efficient data model parsing and validation and interaction with FIWARE 
services' RestAPIs. 

For API interaction, FiLiP relies on the well-known 
[requests](https://docs.python-requests.org/en/latest/) package. 
It is important to understand that we do not in any way restrict any 
features of requests.

Furthermore, FiLiP is designed to help with the fast development of FIWARE-based 
applications and avoid hundreds of lines of boilerplate, but it cannot 
substitute learning the basic concepts behind the used FIWARE components.

## General Motivation

Why implement a client library when clients can be auto-generated 
from openapi documentation? 
A general prerequisite to do so is that the documentation is in depth and of 
good quality. 
While FIWARE generally provides 
[openapi documentation](https://github.com/FIWARE/specifications),
here are some thoughts on the challenges of auto-generating client code from 
these documents:

- Auto-generated code tends to become rather bulky and its quality strongly
  depends on the provided input data.
- Manipulating generated code can result in a big hassle for maintenance if 
  additional features need to be integrated.
- The underlying NGSI (Next Generation Service Interface) for FIWARE is a
  rather generic specification.
  Hence, generated models may also be of generic types as lists
  and dicts in Python. So there is no real benefit.
  Furthermore, there is no chance for reasonable validation and error handling.

## Getting started

The following section shortly describes how to use the library.

### Prerequisites

Since FiLiP is designed as a client library, it requires a server that provides 
the target Service-APIs.
Hence, if you do not yet have a running instance of a FIWARE based platform, 
using docker is the most convenient way to set it up. 
Please check [here](https://github.com/N5GEH/n5geh.platform) for a tutorial 
on this.
If this is not an option for you, FIWARE also provides a testing server.
You can register for a testing account 
[here](https://www.fiware.org/developers/fiware-lab/).
> **Note**: FiLiP is now compatible to [Pydantic V2](https://docs.pydantic.dev/latest/migration/). If your program still require Pydantic V1.x for some reason, please use release [v0.2.5](https://github.com/RWTH-EBC/FiLiP/releases/tag/v0.2.5) or earlier version of FiLiP. Besides, we recommended to set `pydantic~=1.10` in the `requirements.txt`, otherwise Pydantic V2 might still be installed.

#### Supported Python Versions

| Version   | Status         |
|-----------|----------------|
| 3.7      | ❌ Deprecated   |
| 3.8      | ❌ Deprecated   |
| 3.9      | ✅ Tested       |
| 3.10     | ✅ Tested       |
| 3.11     | ✅ Tested       |
| 3.12     | ✅ Tested       |

> ✅ Tested python versions have passed the unittests 

### Installation

The easiest way to install the library is via pip:

````
pip install -U filip
````

If you want to benefit from the latest changes, use the following command 
(This will install the current master branch from this repository):

```
pip install -U git+git://github.com/RWTH-EBC/filip
```

> **Note**: For development, you should install FiLiP in editable mode with the following command:
> ````bash
> pip install -e .[development]
> ````
> The `development` option will install extra libraries required for contribution. Please check the [CONTRIBUTING.md](CONTRIBUTING.md) for more information. 

#### Install extra dependencies for tutorials and examples (optional)

If you need to go through the tutorials or examples, please install filip with extra module ``tutorials``:
````
pip install -U filip[tutorials]
````

#### Install semantics module (optional)

If you want to use the optional [semantics module](filip/semantics), use the following command (This will install the libraries that only required for the semantics module):
````
pip install -U filip[semantics]
````

### Introduction to FIWARE

The following section introduces FIWARE. If you are already familiar with 
FIWARE, you can skip this section and go straight to [Getting Started](#getting-started).

#### What is FIWARE?

FIWARE is a framework of open-source cloud platform components, created 
to facilitate the development of smart solutions within various application 
domains. 
At the moment, the FIWARE 
[catalogue](https://www.fiware.org/developers/catalogue/) contains over 30 
interoperable software modules, so-called Generic Enablers 
(GE) for developing and providing customized IoT platform solutions.

To get familiar with the APIs of the different modules we highly recommend 
checking the 
[step-by-step tutorial](https://fiware-tutorials.readthedocs.io/en/latest/). 
It provides a good overview on FIWARE and its basic usage.
Whereas the tutorial helps to understand most of the general concepts, 
for a deep dive, where you can learn about the components in more detail, 
FIWARE also offers extended lessons through their 
[academy](https://fiware-academy.readthedocs.io/en/latest/index.html/).

However, usually one only requires a small set of components. 
Hence, we recommend using the cited pages only as needed.

#### How to set up a FIWARE platform?

The easiest way to set up a FIWARE platform is by using docker as all GEs are 
open-source and distributed as docker containers on dockerhub.

However, as mentioned before, for most use cases only a subset of GEs is required.
Hence, we wrote a small [tutorial](https://github.com/N5GEH/n5geh.platform) 
explaining how to set up a platform suited for most use cases within the energy 
domain. 

#### FIWARE GEs covered by FiLiP

FiLiP is a library developed on demand.
Hence, we do not aim to cover the APIs of all GEs that are included in the 
[catalogue](https://www.fiware.org/developers/catalogue/). 
This would mean an unnecessary development overhead. 
Therefore, FiLiP currently only covers the APIs of the following GEs:

- NGSIv2 Context Broker for managing context data. We use its 
  reference implementation ORION for testing.
    - [documentation](https://fiware-orion.readthedocs.io/en/master/)
    - [github](https://github.com/telefonicaid/fiware-orion)
    - [swagger](https://swagger.lab.fiware.org/)
    - [NGSI v2 specifications](https://github.com/FIWARE/specifications/tree/master/OpenAPI/ngsiv2)

- NGSI-LD Context Broker for managing context data with Linked Data concept. The functionalities that FiLiP supports are closely aligned with the specification **_NGSI-LD V1.3.1_**, which is according to the FIWARE [catalogue](https://github.com/FIWARE/catalogue#core-context-broker-components) the latest spec version that has been implemented by all three brokers (Orion-LD, Scorpio, and Stellio). We currently use Orion-LD for testing.
    - [github](https://github.com/FIWARE/context.Orion-LD)
    - [swagger](https://swagger.lab.fiware.org/?url=https://raw.githubusercontent.com/FIWARE/specifications/master/OpenAPI/ngsi-ld/full_api.json#/)
  > **Note**: `-experimental` flag need to be set for Orion-LD Context Broker to enable the full functionality. Check this [issue](https://github.com/FIWARE/context.Orion-LD/issues/1648) for more information
    
- IoT-Agents for managing IoT Devices. IoT agents are implemented using 
  the FIWARE IoT Agent Node Lib as a common framework.
    - [documentation](https://iotagent-node-lib.readthedocs.io/en/latest/)
    - [github](https://github.com/telefonicaid/iotagent-node-lib)

    
- IoT-Agent-JSON for managing devices using a JSON message payload protocol 
  format.  
    - [documentation](https://fiware-iotagent-json.readthedocs.io/en/latest/)
    - [github](https://github.com/telefonicaid/iotagent-json)
    - [apiary](https://telefonicaiotiotagents.docs.apiary.io/) 
    (*partly deprecated*)

  Example payload:
  
        {
            "humidity": "45%",
            "temperature": "23",
            "luminosity": "1570"
        }  

- IoT-Agent-Ultralight for managing devices using an Ultralight 2.0 message 
  payload protocol.
  
    - [documentation](https://fiware-iotagent-ul.readthedocs.io/en/latest/)
    - [github](https://github.com/telefonicaid/iotagent-ul)
    - [apiary](https://telefonicaiotiotagents.docs.apiary.io/) 
      (*partly deprecated*)
    
    Example payload:
  
        humidity|45%|temperature|23|luminosity|1570
        
- QuantumLeap for the management of time series data
  
    - [documentation](https://quantumleap.readthedocs.io/en/latest/)
    - [github](https://github.com/FIWARE-GEs/quantum-leap)
    - [swagger](https://app.swaggerhub.com/apis/smartsdk/ngsi-tsdb/0.8.3)

## Structure of FiLiP

![Library Structure](https://raw.githubusercontent.com/RWTH-EBC/FiLiP/master/docs/diagrams/out/architecture.png)


## Documentation

We are still working on the documentation.
You can find our current documentation 
[here](https://rwth-ebc.github.io/FiLiP/master/docs/index.html).

## Running examples

Once you have installed the library, you can check the [examples](/examples)
to learn how to use the different components. 

Currently, we provide basic examples for the usage of FiLiP for the FIWARE 
GEs mentioned above.
We suggest to start in the right order to first understand the 
configuration of clients.
Afterwards, you can start modelling context data and interacting with the context 
broker and use its functionalities before you learn how to connect 
IoT Devices and store historic data.

## Testing

We use unittests to write our test cases.
To test the source code of the library in our CI workflow, the CI 
executes all tests located in the `tests`-directory and prefixed with `test_` .

## Contributing

#### Bug Reports & Feature Requests
The best way to report a bug or request a new feature is to open an issue. Please use one of the available issue templates and provide as much detail as possible.

#### Submitting Pull Requests
We warmly welcome code contributions! If you're planning to contribute, please first read our [Contribution Guide](./CONTRIBUTING.md) for details on our development workflow, coding standards, and how to submit a pull request.

For other inquiries, you can still contact us via [ebc-tools@eonerc.rwth-aachen.de](mailto:ebc-tools@eonerc.rwth-aachen.de).

## Authors

* [Thomas Storek](https://github.com/tstorek) 
* [Junsong Du](https://www.ebc.eonerc.rwth-aachen.de/cms/E-ON-ERC-EBC/Das-Institut/Mitarbeiter/Digitale-Energie-Quartiere/~trcib/Du-Junsong/lidx/1/) (corresponding)
* [Saira Bano](https://www.ebc.eonerc.rwth-aachen.de/cms/E-ON-ERC-EBC/Das-Institut/Mitarbeiter/Systemadministration/~ohhca/Bano-Saira/)

## Alumni

* Jeff Reding
* Felix Rehmann
* Daniel Nikolay
* Sebastian Blechmann

## References
If you use FiLiP in your work, please cite the JOSS paper:
```bibtex
@article{Storek2024,
doi = {10.21105/joss.06953},
url = {https://doi.org/10.21105/joss.06953},
year = {2024},
publisher = {The Open Journal},
volume = {9},
number = {101},
pages = {6953},
author = {Storek, Thomas and Du, Junsong and Blechmann, Sebastian and Streblow, Rita and Müller, Dirk},
title = {FiLiP: A python software development kit (SDK) for accelerating the development of services based on FIWARE IoT platform},
journal = {Journal of Open Source Software}
} 
```

We also want to refer to publications that presented or applied the library:

- S. Blechmann, I. Sowa, M. H. Schraven, R. Streblow, D. Müller & A. Monti. Open source platform application for smart building and smart grid controls. Automation in Construction 145 (2023), 104622. ISSN: 0926-5805. https://doi.org/10.1016/j.autcon.2022.104622        

- Haghgoo, M., Dognini, A., Storek, T., Plamanescu, R, Rahe, U., 
  Gheorghe, S, Albu, M., Monti, A., Müller, D. (2021) A cloud-based service-oriented architecture to unlock smart energy services
  https://www.doi.org/10.1186/s42162-021-00143-x      

- Baranski, M., Storek, T. P. B., Kümpel, A., Blechmann, S., Streblow, R., 
Müller, D. et al.,
(2020). National 5G Energy Hub : Application of the Open-Source Cloud Platform 
FIWARE for Future Energy Management Systems. 
https://doi.org/10.18154/RWTH-2020-07876      

- T. Storek, J. Lohmöller, A. Kümpel, M. Baranski & D. Müller (2019). 
Application of the open-source cloud platform FIWARE for future building 
energy management systems. 
Journal of Physics: 
Conference Series, 1343, 12063. https://doi.org/10.1088/1742-6596/1343/1/012063     

## License

This project is licensed under the BSD License - see the [LICENSE](LICENSE.md) file for details.

## Copyright

<a href="https://www.ebc.eonerc.rwth-aachen.de/"> <img alt="EBC" src="https://www.ebc.eonerc.rwth-aachen.de/global/show_picture.asp?id=aaaaaaaaaakevlz" height="100"> </a>

2021-2025, RWTH Aachen University, E.ON Energy Research Center, Institute for Energy 
Efficient Buildings and Indoor Climate

[Institute for Energy Efficient Buildings and Indoor Climate (EBC)](https://www.ebc.eonerc.rwth-aachen.de)  
[E.ON Energy Research Center (E.ON ERC)](https://www.eonerc.rwth-aachen.de)  
[RWTH University Aachen, Germany](https://www.rwth-aachen.de)

## Disclaimer

This project is part of the cooperation between the RWTH Aachen University and 
the Research Centre Jülich.

<a href="https://www.jara.org/de/forschung/jara-energy"> <img alt="JARA 
ENERGY" src="https://raw.githubusercontent.com/RWTH-EBC/FiLiP/master/docs/logos/LogoJARAEnergy.jpg" height="100"> </a>

## Related projects

<a href="https://n5geh.de/"> <img alt="National 5G Energy Hub" 
src="https://avatars.githubusercontent.com/u/43948851?s=200&v=4" height="100"></a>

<a href="https://fismep.de/"> <img alt="FISMEP" 
src="https://raw.githubusercontent.com/RWTH-EBC/FiLiP/master/docs/logos/FISMEP.png" 
height="100"></a>


## Acknowledgments

We gratefully acknowledge the financial support of the Federal Ministry <br /> 
for Economic Affairs and Climate Action (BMWK), promotional references 
03ET1495A, 03ET1551A, 0350018A, 03ET1561B, 03EN1030B.

<a href="https://www.bmwi.de/Navigation/EN/Home/home.html"> <img alt="BMWK" 
src="https://raw.githubusercontent.com/RWTH-EBC/FiLiP/master/docs/logos/bmwi_logo_en.png" height="100"> </a>

This project has received funding in the framework of the joint programming initiative ERA-Net Smart Grids Plus, with support from the European Union’s Horizon 2020 research and innovation programme.

<a href="https://www.eranet-smartgridsplus.eu/"> <img alt="ERANET" 
src="https://fismep.de/wp-content/uploads/2017/09/SmartGridsPlus_rgb-300x55.jpg" height="100"> </a>
