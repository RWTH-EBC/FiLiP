import logging
from unittest import TestCase
from filip.config import settings


class TestLoggingConfig(TestCase):
    def setUp(self) -> None:
        pass
        #self.logger.propagate = False
        #logging.basicConfig()

    def test_overwrite_config(self):
        # Try to set logging level before calling logging.basisConfig()
        # Since no handler is configured this will fail
        self.logger = logging.getLogger(
            name=f"{__package__}.{self.__class__.__name__}")
        self.logger.warning("Trying to set LOG_LEVEL to '%s' via settings "
                            "before calling basicConfig. This will fail "
                            "because no handler is added to the logger",
                            settings.LOG_LEVEL)
        settings.LOG_LEVEL = logging.DEBUG
        #self.logger.setLevel(level=settings.LOG_LEVEL)
        # The next line will not show up!
        self.logger.info("Current LOG_LEVEL is '%s'", self.logger.level)

        # Try to set logging level before calling logging.basisConfig()
        # but adding a handler before.
        self.logger.handlers.clear()
        handler = logging.StreamHandler()
        formatter = logging.Formatter(fmt=settings.LOG_FORMAT)
        handler.setFormatter(formatter)
        self.logger.info("Set LOG_LEVEL to '%s' via settings and adding a "
                         "handler before. ",
                         settings.LOG_LEVEL)
        self.logger.addHandler(handler)
        self.logger.setLevel(level=settings.LOG_LEVEL)
        self.logger.info("Current LOG_LEVEL has changed to '%s'",
                         self.logger.level)
        # The next line will not show up!
        self.logger.debug("Current LOG_LEVEL is '%s'", self.logger.level)

        # Try to set loglevel via basicConfig
        new_loglevel = logging.WARNING
        self.logger.info("Set LOG_LEVEL to '%s' via basicConfig", new_loglevel)
        #logging.basicConfig(level=new_loglevel,
        #                    format='%(asctime)s : %(name)s : %(levelname)s : '
        #                           '%(message)s')
        logger = logging.getLogger()
        handler = logging.StreamHandler()
        logger.addHandler(handler)
        logger.setLevel('DEBUG')
        logger.debug('Initialize root logger')


        # This message should not show up anymore but it does because the
        # loggers are detached and we need to delete the handler first
        self.logger.info("Current LOG_LEVEL asfasf '%s'", self.logger.level)

    def tearDown(self) -> None:
        pass