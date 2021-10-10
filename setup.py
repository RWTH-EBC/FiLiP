"""Setup.py script for the FiLiP-Library"""

import setuptools

# read the contents of your README file
from pathlib import Path
readme_path = Path(__file__).parent.joinpath("README.md")
LONG_DESCRIPTION = readme_path.read_text()

INSTALL_REQUIRES = ['aenum',
                    'requests',
                    'rapidfuzz',
                    'PyYAML',
                    'pandas>=1.2',
                    'datamodel-code-generator>=0.10.2',
                    'pandas-datapackage-reader>=0.18.0',
                    'pydantic[dotenv]>=1.7.2',
                    'tables']

SETUP_REQUIRES = INSTALL_REQUIRES.copy()

setuptools.setup(
    name='filip',
    version='0.1.8',
    author='RWTH Aachen University, E.ON Energy Research Center, Institute\
        of Energy Efficient Buildings and Indoor Climate',
    author_email='tstorek@eonerc.rwth-aachen.de',
    description='[FI]WARE [li]brary for [P]ython',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/RWTH-EBC/filip",
    project_urls={"Documentation": "https://ebc.pages.rwth-aachen.de/EBC_all/"
                                   "fiware/filip/development/docs/index.html"},
    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    classifiers=['Development Status :: 3 - Beta',
                 'Topic :: Scientific/Engineering',
                 'Intended Audience :: Science/Research',
                 'Programming Language :: Python :: 3.7',
                 'Programming Language :: Python :: 3.8',
                 "License :: OSI Approve :: BSD 3-Clause License"],
    keywords=['iot', 'fiware', 'semantic'],
    packages=setuptools.find_packages(exclude=['tests','tests.*','img']),
    setup_requires=SETUP_REQUIRES,
    install_requires=INSTALL_REQUIRES,
    python_requires=">=3.7",
)
