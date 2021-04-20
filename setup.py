import setuptools

INSTALL_REQUIRES = ['aenum',
                    'requests',
                    'fuzzywuzzy',
                    'PyYAML',
                    'pandas>=1.2',
                    'datamodel-code-generator>=0.10.2',
                    'pandas-datapackage-reader>=0.18.0',
                    'pydantic[dotenv]>=1.7.2',
                    'requests_oauthlib',
                    'authlib']

SETUP_REQUIRES = INSTALL_REQUIRES.copy()


setuptools.setup(
    name='filip',
    version='0.1',
    description='[FI]WARE [li]brary for [P]ython',
    author='RWTH Aachen University, E.ON Energy Research Center, Institute\
                     of Energy Efficient Buildings and Indoor Climate',
    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    classifiers=['Programming Language :: Python :: 3.7',
                 'Programming Language :: Python :: 3.8',
                 'Programming Language :: Python :: 3.9'],
    author_email='tstorek@eonerc.rwth-aachen.de',
    packages=setuptools.find_packages(exclude=['img']),
    setup_requires=SETUP_REQUIRES,
    install_requires=INSTALL_REQUIRES,
)
