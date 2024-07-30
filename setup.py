"""Setup.py script for the FiLiP-Library"""

import setuptools

# read the contents of your README file
from pathlib import Path
readme_path = Path(__file__).parent.joinpath("README.md")
LONG_DESCRIPTION = readme_path.read_text()

INSTALL_REQUIRES = ['aenum~=3.1.15',
                    'datamodel_code_generator[http]~=0.25.0',
                    'paho-mqtt~=2.0.0',
                    'pandas_datapackage_reader~=0.18.0',
                    'pydantic>=2.5.2,<2.7.0',
                    'pydantic-settings>=2.0.0,<2.3.0',
                    'geojson_pydantic~=1.0.2',
                    'stringcase>=1.2.0',
                    'rdflib~=6.0.0',
                    'regex~=2023.10.3',
                    'requests~=2.31.0',
                    'rapidfuzz~=3.4.0',
                    'geojson-pydantic~=1.0.2',
                    'wget~=3.2',
                    'pyjexl~=0.3.0']

SETUP_REQUIRES = INSTALL_REQUIRES.copy()

VERSION = '0.5.0'

setuptools.setup(
    name='filip',
    version=VERSION,
    author='RWTH Aachen University, E.ON Energy Research Center, Institute\
        of Energy Efficient Buildings and Indoor Climate',
    author_email='tstorek@eonerc.rwth-aachen.de',
    description='[FI]WARE [Li]brary for [P]ython',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/RWTH-EBC/filip",
    download_url=f"https://github.com/RWTH-EBC/FiLiP/archive/refs/tags/v{VERSION}.tar.gz",
    project_urls={
        "Documentation":
            "https://rwth-ebc.github.io/FiLiP/master/docs/index.html",
        "Source":
            "https://github.com/RWTH-EBC/filip",
        "Download":
            f"https://github.com/RWTH-EBC/FiLiP/archive/refs/tags/v{VERSION}.tar.gz"},
    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    classifiers=['Development Status :: 3 - Alpha',
                 'Topic :: Scientific/Engineering',
                 'Intended Audience :: Science/Research',
                 'Programming Language :: Python :: 3.8',
                 'Programming Language :: Python :: 3.9',
                 'Programming Language :: Python :: 3.10',
                 'Programming Language :: Python :: 3.11',
                 "License :: OSI Approved :: BSD License"],
    keywords=['iot', 'fiware', 'semantic'],
    packages=setuptools.find_packages(exclude=['tests',
                                               'tests.*',
                                               'img',
                                               'tutorials.*',
                                               'tutorials']),
    package_data={'filip': ['data/unece-units/*.csv']},
    setup_requires=SETUP_REQUIRES,
    # optional modules
    extras_require={
        "semantics": ["igraph~=0.11.2"],
        ":python_version < '3.9'": ["pandas~=1.3.5"],
        ":python_version >= '3.9'": ["pandas~=2.1.4"]
    },
    install_requires=INSTALL_REQUIRES,
    python_requires=">=3.8",

)
