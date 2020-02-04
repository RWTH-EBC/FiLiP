import logging

datamanger = None
datamanager = None  # Default value for datamanager object
default_loglevel = 'DEBUG' # Default logLevel
if datamanager == None:
    logging.basicConfig(level=default_loglevel,
                        format='%(asctime)s %(name)s [%(levelname)s]: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

__version__ = '0.1'
__all__ = ["orion", "iot", "subscription", "timeseries"]

