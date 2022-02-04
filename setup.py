"""Setup.py script for the FiLiP-Library"""

import setuptools

# read the contents of your README file
from pathlib import Path
readme_path = Path(__file__).parent.joinpath("README.md")
LONG_DESCRIPTION = readme_path.read_text()

INSTALL_REQUIRES = ['aenum',
                    'datamodel_code_generator[http]>=0.11.16',
                    'paho-mqtt>=1.6.1',
                    'pandas>=1.2',
                    'pandas-datapackage-reader>=0.18.0',
                    'pydantic[dotenv]>=1.7.2',
                    'PyYAML',
                    'stringcase>=1.2.0',
                    'igraph==0.9.8',
                    'rdflib~=6.0.0',
                    'regex',
                    'requests',
                    'rapidfuzz',
                    'wget']

SETUP_REQUIRES = INSTALL_REQUIRES.copy()

setuptools.setup(
    name='filip',
    version='0.2.1',
    author='RWTH Aachen University, E.ON Energy Research Center, Institute\
        of Energy Efficient Buildings and Indoor Climate',
    author_email='tstorek@eonerc.rwth-aachen.de',
    description='[FI]WARE [Li]brary for [P]ython',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/RWTH-EBC/filip",
    download_url="https://github.com/RWTH-EBC/FiLiP/archive/refs/tags/v0.2.1.tar.gz",
    project_urls={
        "Documentation":
            "https://ebc.pages.rwth-aachen.de/EBC_all/github_ci/FiLiP/master/docs/index.html",
        "Source":
            "https://github.com/RWTH-EBC/filip",
        "Download":
            "https://github.com/RWTH-EBC/FiLiP/archive/refs/tags/v0.2.1.tar.gz"},
    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    classifiers=['Development Status :: 3 - Beta',
                 'Topic :: Scientific/Engineering',
                 'Intended Audience :: Science/Research',
                 'Programming Language :: Python :: 3.7',
                 'Programming Language :: Python :: 3.8',
                 "License :: OSI Approve :: BSD 3-Clause License"],
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
