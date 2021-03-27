import logging
import requests
from filip.core.models import FiwareHeader


class BaseClient:
    """
    This class implements an base client for all derived api-clients.
    """

    def __init__(self,
                 session: requests.Session = None,
                 fiware_header: FiwareHeader = None):
        """

        Args:
            session: request session object. This is required for reusing
                the same connection
            fiware_header: Fiware header object required for multi tenancy
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        # TODO: Double Check Header Handling
        self.session = session or requests.Session()
        self.headers = dict()
        if not fiware_header:
            fiware_header = FiwareHeader()
        self.headers.update(fiware_header.dict(by_alias=True))

    # Context Manager Protocol
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def log_error(self,
                  e: requests.RequestException,
                  msg: str = None) -> None:
        """

        Args:
            e: Request Error
            msg:

        Returns:

        """
        if e.response and msg:
            self.logger.error(f"{msg} \n Reason: {e.response.text}")
        elif e.response and not msg:
            self.logger.error({e.response.text})
        elif not e.response and msg:
            self.logger.error(f"{msg} \n Reason: {e}")
        else:
            self.logger.error({e})


    def close(self):
        self.session.close()
