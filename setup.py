import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    LONG_DESCRIPTION = fh.read()


INSTALL_REQUIRES = ['aenum',
                    'requests',
                    'fuzzywuzzy',
                    'PyYAML',
                    'pandas>=1.2',
                    'datamodel-code-generator>=0.10.2',
                    'pandas-datapackage-reader>=0.18.0',
                    'pydantic[dotenv]>=1.7.2',
                    'tables',
                    'requests_oauthlib',
                    'authlib']

SETUP_REQUIRES = INSTALL_REQUIRES.copy()


setuptools.setup(
    name='filip',
    version='0.1.2',
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
    classifiers=['Programming Language :: Python :: 3.7',
                 'Programming Language :: Python :: 3.8',
                 'Programming Language :: Python :: 3.9',
                 "License :: OSI Approve :: BSD 3-Clause License"],
    packages=setuptools.find_packages(exclude=['img']),
    setup_requires=SETUP_REQUIRES,
    install_requires=INSTALL_REQUIRES,
    python_requires=">=3.7",
)
