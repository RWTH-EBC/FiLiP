"""
Test module for logging functionality
"""
import logging
from unittest import TestCase


class TestLoggingConfig(TestCase):
    """
    Test case for logging functionality
    """
    def setUp(self) -> None:
        self.logger = logging.getLogger(
            name=f"{__package__}.{self.__class__.__name__}")

    def test_overwrite_config(self):
        """
        Tests to overwrite the logger configurations

        Returns:
            None
        """

        # Try to set logging level before calling logging.basisConfig()
        # Since no handler is configured this will fail
        self.logger = logging.getLogger(
            name=f"{__package__}.{self.__class__.__name__}")
        self.logger.warning("Trying to set log_level to '%s' via settings "
                            "before calling basicConfig. This will fail "
                            "because no handler is added to the logger",
                            logging.DEBUG)
        self.logger.setLevel(level=logging.DEBUG)
        # The next line will not show up!
        self.logger.info("Current LOG_LEVEL is '%s'", self.logger.level)

        # Try to set logging level before calling logging.basisConfig()
        # but adding a handler before.
        self.logger.handlers.clear()
        handler = logging.StreamHandler()
        formatter = logging.Formatter(fmt='Custom Logging Stream %(asctime)s - '
                                          '%(name)s - '
                                          '%(levelname)s : %(message)s')
        handler.setFormatter(formatter)
        self.logger.info("Set LOG_LEVEL to '%s' via settings and adding a "
                         "handler before. ",
                         logging.DEBUG)
        self.logger.addHandler(handler)
        self.logger.setLevel(level=logging.DEBUG)
        self.logger.info("Current LOG_LEVEL has changed to '%s'",
                         self.logger.level)
        # The next line will not show up!
        self.logger.debug("Current LOG_LEVEL is '%s'", self.logger.level)

        # Try to set loglevel via basicConfig
        new_loglevel = logging.WARNING
        self.logger.info("Set LOG_LEVEL to '%s' via basicConfig", new_loglevel)
        # logging.basicConfig(level=new_loglevel,
        #                    format='%(asctime)s : %(name)s : %(levelname)s : '
        #                           '%(message)s')
        logger = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = logging.Formatter(fmt='Root Stream %(asctime)s - '
                                          '%(name)s - '
                                          '%(levelname)s : %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel('DEBUG')
        logger.debug('Initialize root logger')
        # This message will show up twice because now a handler is configured
        # in the root logger and all messages will be forwarded
        # but it does because the
        # loggers are detached and we need to delete the handler first
        self.logger.info("Current LOG_LEVEL '%s' (this will appear twice)",
                         self.logger.level)

    def tearDown(self) -> None:
        pass
