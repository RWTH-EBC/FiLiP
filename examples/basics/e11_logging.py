"""
# Example to show we can make use of python's logging when using filip.
# The configuration is totally up to the user because FiLiP should not
# interfere with the user's final application and preferences.
# Each module has its own logger but does not configure any streams and
# therefore reuses the streams of the root logger.
"""

# import python's built-in logging implementation
import logging

# import an api client from filip as example
from filip.clients.ngsi_v2 import ContextBrokerClient

# setting up the basic configuration of the logging system. Please check the
# official documentation and the functions docstrings for more details.
# Handling for 'handlers' in the logging system is not trivial.
# It is also important to know that this function should only be called once in
# your application. Since FiLiP is an SDK that should help to implement other
# services, we do not call this function anywhere in our code.
# Hence, it is up to the user to configure the logging system.

# In this example we will simply change the log level and the log format.
logging.basicConfig(
    level="DEBUG", format="%(asctime)s %(name)s %(levelname)s: %(message)s"
)

# You need to change the output
ocb = ContextBrokerClient(url="http://<PleaseChange.Me>")
ocb.get_version()
