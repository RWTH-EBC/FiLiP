![E.ON EBC RWTH Aachen University](https://raw.githubusercontent.com/N5GEH/n5geh.tools.FiLiP/development/docs/logos/EBC_Logo.png)

# FiLiP

[![pylint](https://ebc.pages.rwth-aachen.de/EBC_all/github_ci/ebcpy/master/pylint/pylint.svg )](https://ebc.pages.rwth-aachen.de/EBC_all/github_ci/FiLiP/master/pylint/pylint.html)
[![Documentation](https://ebc.pages.rwth-aachen.de/EBC_all/github_ci/FiLiP/development/docs/doc.svg)](https://ebc.pages.rwth-aachen.de/EBC_all/github_ci/FiLiP/master/docs/index.html)
[![coverage](https://ebc.pages.rwth-aachen.de/EBC_all/github_ci/ebcpy/master/coverage/badge.svg)](https://ebc.pages.rwth-aachen.de/EBC_all/github_ci/FiLiP/master/coverage)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![build](https://ebc.pages.rwth-aachen.de/EBC_all/github_ci/ebcpy/master/build/build.svg)](https://ebc.pages.rwth-aachen.de/EBC_all/github_ci/FiLiP/master/build/build.svg)

FiLiP (Fiware Library for Python) is a python software development kit (SDK) for 
accelerating the development of web services that use Fiware's Generic 
Enablers (GEs) as backend.

Is it mainly based on the [Pydantic](https://pydantic-docs.helpmanual.io/) 
package which is sophisticated library for data validation and settings 
management using python type annotations.
Pydantic enforces type hints at runtime, and provides user friendly errors 
when data is invalid.
We mainly use Pydantic model to build our own data model structure required 
for efficient data model parsing and validation and interaction with FIWARE 
services' RestAPIs.

For API interaction FiLiP relies on the well-known 
[requests](https://docs.python-requests.org/en/latest/) package. 
It is important to understand that we do not in any way restrict any 
features of requests.

Furthermore, FiLiP is designed to help with fast development of FIWARE based 
application and avoid hundreds of lines of boilerplate, but it cannot 
substitute to learn the basic concepts behind the used FIWARE components.

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
- The underlying NGSI (New Generation Service Interface) for FIWARE is a
  rather generic specification.
  Hence, generated models may also be of generic types as lists
  and dicts in Python. So there is no real benefit.
  Furthermore, there is no chance for reasonable validation and error handling.

## Getting started

The following section shortly describes use of the library.

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

### Installation

The easiest way to install the library is via pip:

```
pip install -U git+git://github.com/RWTH-EBC/filip
```

If you want to benefit from the latest changes, use the development branch:

```
pip install -U git+git://github.com/RWTH-EBC/filip@development
```

**Note**: We are currently working bringing the library to PyPi to enable 
easy package installation without using git

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

![Library Structure](https://github.com/RWTH-EBC/FiLiP/blob/master/docs/diagrams/out/architecture.png)


## Documentation

We are still working on the documentation.
You can find our current documentation 
[here](https://ebc.pages.rwth-aachen.de/EBC_all/github_ci/FiLiP/development/docs/index.html).

## Running examples

Once you have installed the library, you can check the [examples](/examples)
to learn how to use the different components. 

Currently, we provide basic examples for the usage of FiLiP for the FIWARE 
GEs mentioned above.
We suggest to start in the right order to first understand the 
configuration of clients.
Afterwards, you can start modelling context data and interact the context 
broker and use its functionalities before you learn how to connect 
IoT Devices and store historic data.

## Testing

We use unittests to write our test cases.
To test the source code of the library in our a CI workflow, the CI does 
execute all tests located in the `tests`-directory and prefixed with `test_` .

## How to contribute

Please see our [contribution guide](./CONTRIBUTING.md) for more details on 
how you can contribute to this project.

## Authors

* [Thomas Storek](https://www.ebc.eonerc.rwth-aachen.de/cms/E-ON-ERC-EBC/Das-Institut/Mitarbeiter/Team2/~lhda/Thomas-Storek/?lidx=1) (corresponding)
* [Saira Bano](https://www.ebc.eonerc.rwth-aachen.de/cms/E-ON-ERC-EBC/Das-Institut/Mitarbeiter/Systemadministration/~ohhca/Bano-Saira/)
* [Daniel Nikolay](https://www.ebc.eonerc.rwth-aachen.de/cms/E-ON-ERC-EBC/Das-Institut/Mitarbeiter/Systemadministration/~qcqxq/Nikolay-Daniel/)
* [Stephan Göbel](https://www.ebc.eonerc.rwth-aachen.de/cms/E-ON-ERC-EBC/Das-Institut/Mitarbeiter/Team3/~ccdhp/Goebel-Stephan/)
* [Sebastian Borges](https://www.ebc.eonerc.rwth-aachen.de/cms/E-ON-ERC-EBC/Das-Institut/Mitarbeiter/Team3/~mvoee/Borges-Sebastian/)


## Alumni

* Jeff Reding
* Felix Rehmann

## References

We presented or applied the library in the following publications:

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

This project is licensed under the BSD License - see the [LICENSE](LICENSE) file for details.

## Copyright

<a href="https://www.ebc.eonerc.rwth-aachen.de/"> <img alt="EBC" src="https://www.ebc.eonerc.rwth-aachen.de/global/show_picture.asp?id=aaaaaaaaaakevlz" height="100"> </a>

2021, RWTH Aachen University, E.ON Energy Research Center, Institute for Energy 
Efficient Buildings and Indoor Climate

[Institute for Energy Efficient Buildings and Indoor Climate (EBC)](http://www.ebc.eonerc.rwth-aachen.de)  
[E.ON Energy Research Center (E.ON ERC)](http://www.eonerc.rwth-aachen.de)  
[RWTH University Aachen, Germany](http://www.rwth-aachen.de)

## Disclaimer

This project is part of cooperation between the RWTH Aachen University and 
the Research Centre Jülich.

<a href="https://www.jara.org/de/forschung/jara-energy"> <img alt="JARA 
ENERGY" src="https://github.com/RWTH-EBC/FiLiP/tree/master/docs/logos/LogoJARAEnergy.jpg" height="100"> </a>

## Related projects

<a href="https://n5geh.de/"> <img alt="National 5G Energy Hub" 
src="https://avatars.githubusercontent.com/u/43948851?s=200&v=4" height="100"></a>

<a href="http://fismep.de/"> <img alt="National 5G Energy Hub" 
src="http://www.fismep.de/wp-content/uploads/2017/11/FISMEP_email_signature
-1.png" height="100" ></a>



## Acknowledgments

We gratefully acknowledge the financial support of the Federal Ministry <br /> 
for Economic Affairs and Energy (BMWi), promotional reference 03ET1561B.

<a href="https://www.bmwi.de/Navigation/EN/Home/home.html"> <img alt="BMWE" src="https://www.bmwi.de/SiteGlobals/BMWI/StyleBundles/Bilder/bmwi_logo_en.svgz?__blob=normal&v=10" height="100"> </a>

This project has received funding in the framework of the joint programming initiative ERA-Net Smart Grids Plus, with support from the European Union’s Horizon 2020 research and innovation programme.

<a href="http://www.eranet-smartgridsplus.eu/"> <img alt="ERANET" 
src="http://fismep.de/wp-content/uploads/2017/09/SmartGridsPlus_rgb-300x55.jpg" height="100"> </a>



