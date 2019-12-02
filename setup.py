import setuptools

INSTALL_REQUIRES = ['requests',
                    'fuzzywuzzy',
                    'PyYAML']

SETUP_REQUIRES = INSTALL_REQUIRES.copy()


setuptools.setup(
    name='filip',
    version='1.0',
    description='[FI]WARE [li]brary in [p]ython',
    author='RWTH Aachen University, E.ON Energy Research Center, Institute\
                     of Energy Efficient Buildings and Indoor Climate',
    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    classifiers=['Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7', ],
    author_email='tstorek@eonerc.rwth-aachen.de',
    packages=setuptools.find_packages(exclude=['img']),
    setup_requires=SETUP_REQUIRES,
    install_requires=INSTALL_REQUIRES,
)
