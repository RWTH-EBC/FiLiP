"""Setup.py script for the FiLiP-Library"""

import setuptools

# read the contents of your README file
from pathlib import Path
readme_path = Path(__file__).parent.joinpath("README.md")
LONG_DESCRIPTION = readme_path.read_text()

INSTALL_REQUIRES = ['aenum~=3.1.15',
                    'datamodel_code_generator[http]~=0.25.0',
                    'paho-mqtt~=1.6.1',
                    'pandas~=2.1.3',
                    'pandas_datapackage_reader~=0.18.0',
                    'pydantic~=2.5.2',
                    'pydantic-settings~=2.1.0',
                    'stringcase>=1.2.0',
                    # semantics module
                    # 'igraph==0.9.8',
                    # 'rdflib~=6.0.0',
                    'regex~=2023.10.3',
                    'requests~=2.31.0',
                    'rapidfuzz~=3.5.2',
                    'wget~=3.2']

SETUP_REQUIRES = INSTALL_REQUIRES.copy()

VERSION = '0.3.0'

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
            "https://ebc.pages.rwth-aachen.de/EBC_all/github_ci/FiLiP/master/docs/index.html",
        "Source":
            "https://github.com/RWTH-EBC/filip",
        "Download":
            f"https://github.com/RWTH-EBC/FiLiP/archive/refs/tags/v{VERSION}.tar.gz"},
    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    classifiers=['Development Status :: 3 - Alpha',
                 'Topic :: Scientific/Engineering',
                 'Intended Audience :: Science/Research',
                 'Programming Language :: Python :: 3.7',
                 'Programming Language :: Python :: 3.8',
                 'Programming Language :: Python :: 3.9',
                 "License :: OSI Approved :: BSD License"],
    keywords=['iot', 'fiware', 'semantic'],
    packages=setuptools.find_packages(exclude=['tests',
                                               'tests.*',
                                               'img',
                                               'tutorials.*',
                                               'tutorials']),
    package_data={'filip': ['data/unece-units/*.csv']},
    setup_requires=SETUP_REQUIRES,
    install_requires=INSTALL_REQUIRES,
    python_requires=">=3.7",

)
