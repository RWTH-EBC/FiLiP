import validators
import logging
import requests
from filip.core.models import FiwareHeader


class BaseClient:
    """
    This class implements an base client for all derived api-clients.
    """

    def __init__(self, *,
                 url: str = None,
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
        if url:
            if not validators.url(url):
                raise ValueError(f"Found invalid url scheme for "
                                 f"{self.__class__.__name__}")
        self.base_url = url
        self.session = session or requests.Session()
        if not fiware_header:
            fiware_header = FiwareHeader()
        self.headers.update(fiware_header.dict(by_alias=True))

    # Context Manager Protocol
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def headers(self):
        return self.session.headers

    def log_error(self,
                  err: requests.RequestException,
                  msg: str = None) -> None:
        """

        Args:
            err: Request Error
            msg: error message from calling function

        Returns:

        """
        if err.response and msg:
            self.logger.error("%s \n Reason: %s", msg, err.response.text)
        elif err.response and not msg:
            self.logger.error("%s", err.response.text)
        elif not err.response and msg:
            self.logger.error("%s \n Reason: %s", msg, err)
        else:
            self.logger.error(err)


    def close(self):
        self.session.close()
