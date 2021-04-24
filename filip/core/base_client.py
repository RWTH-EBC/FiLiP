"""
Base client module
"""
import logging
import requests
from typing import Dict, Union
from filip.core.models import FiwareHeader
from filip.utils import validate_url


class BaseClient:

    """
    This class implements an base client for all derived api-clients.
    """

    def __init__(self,
                 url: str = None,
                 *,
                 session: requests.Session = None,
                 fiware_header: Union[Dict, FiwareHeader] = None):
        """

        Args:
            session: request session object. This is required for reusing
                the same connection
            fiware_header: Fiware header object required for multi tenancy
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        # TODO: Double Check Header Handling
        validate_url(url)
        self.base_url = url
        self.session = session or requests.Session()
        if not fiware_header:
            self.fiware_headers = FiwareHeader()
        else:
            self.fiware_headers = fiware_header

    # Context Manager Protocol
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def fiware_headers(self):
        return self._fiware_headers.copy()

    @fiware_headers.setter
    def fiware_headers(self, headers: Union[Dict, FiwareHeader]):
        if isinstance(headers, FiwareHeader):
            self._fiware_headers = headers
        elif isinstance(headers, dict):
            self._fiware_headers = FiwareHeader.parse_obj(headers)
        elif isinstance(headers, str):
            self._fiware_headers = FiwareHeader.parse_raw(headers)
        else:
            raise TypeError(f'Invalid headers! {type(headers)}')
        self.headers.update(self.fiware_headers.dict(by_alias=True))

    @property
    def fiware_service(self):
        return self.fiware_headers.service_path

    @fiware_service.setter
    def fiware_service(self, service: str):
        self._fiware_headers.service = service
        self.headers.update(self.fiware_headers.dict(by_alias=True))

    @property
    def fiware_service_path(self):
        return self.fiware_headers.service_path

    @fiware_service_path.setter
    def fiware_service_path(self, service_path: str):
        self._fiware_headers.service_path = service_path
        self.headers.update(self.fiware_headers.dict(by_alias=True))

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
        if err.response.text and msg:
            self.logger.error("%s \n Reason: %s", msg, err.response.text)
        elif err.response.text and not msg:
            self.logger.error("%s", err.response.text)
        elif not err.response and msg:
            self.logger.error("%s \n Reason: %s", msg, err)
        else:
            self.logger.error(err)

    def close(self):
        self.session.close()
