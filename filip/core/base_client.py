"""
Base client module
"""
import logging
import requests
from typing import Dict, ByteString, List, IO, Tuple, Union
from filip.core.models import FiwareHeader
from filip.utils import validate_url


class BaseClient:
    """
    Base client for all derived api-clients.
    """
    def __init__(self,
                 url: str = None,
                 *,
                 session: requests.Session = None,
                 reuse_session: bool = False,
                 fiware_header: Union[Dict, FiwareHeader] = None,):
        """
        Args:
            session: request session object. This is required for reusing
                the same connection
            fiware_header: Fiware header object required for multi tenancy
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        # TODO: Double Check Header Handling
        if url:
            validate_url(url)
            self.base_url = url

        if session or reuse_session:
            self.session = session or requests.Session()
        else:
            self.session = None
            self._headers = {}

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
        """
        Return current session headers
        Returns:
            dict with headers
        """
        if self.session:
            return self.session.headers
        return self._headers

    # modification to requests api
    def get(self, url: str, params: Dict = None, **kwargs) -> requests.Response:
        """
        Sends a GET request either using the provided session or the single
        session.

        Args:
            url (str): URL for the new :class:`Request` object.
            params (optional): (optional) Dictionary, list of tuples or bytes
                to send in the query string for the :class:`Request`.
            **kwargs: Optional arguments that ``request`` takes.

        Returns:
            requests.Response
        """
        if self.session:
            return self.session.get(url=url, params=params, **kwargs)
        return requests.get(url=url, params=params, **kwargs)

    def options(self, url: str, **kwargs) -> requests.Response:
        """
        Sends an OPTIONS request either using the provided session or the
        single session.

        Args:
            url (str):
            **kwargs: Optional arguments that ``request`` takes.

        Returns:
            requests.Response
        """
        if self.session:
            return self.session.options(url=url, **kwargs)
        return requests.options(url=url, **kwargs)

    def head(self, url: str, **kwargs) -> requests.Response:
        """
        Sends a HEAD request either using the provided session or the
        single session.

        Args:
            url (str): URL for the new :class:`Request` object.
            params (optional): (optional) Dictionary, list of tuples or bytes
                to send in the query string for the :class:`Request`.
            **kwargs: Optional arguments that ``request`` takes.

        Returns:
            requests.Response
        """
        if self.session:
            return self.session.head(url=url, **kwargs)
        return requests.head(url=url, **kwargs)

    def post(self,
             url: str,
             data: Union[Dict, ByteString, List[Tuple], IO] = None,
             json: str = None,
             **kwargs) -> requests.Response:
        """
        Sends a POST request either using the provided session or the
        single session.
        Args:
            url: URL for the new :class:`Request` object.
            data (Union[Dict, ByteString, List[Tuple], IO]):
                Dictionary, list of tuples, bytes, or file-like
                object to send in the body of the :class:`Request`.
            json (JSON): json data to send in the body of the :class:`Request`.
            **kwargs: Optional arguments that ``request`` takes.

        Returns:

        """
        if self.session:
            return self.session.post(url=url, data=data, json=json, **kwargs)
        return requests.post(url=url, data=data, json=json, **kwargs)

    def put(self,
            url: str,
            data: Union[Dict, ByteString, List[Tuple], IO] = None,
            json: str = None,
            **kwargs) -> requests.Response:
        """
        Sends a PUT request either using the provided session or the
        single session.

        Args:
            url: URL for the new :class:`Request` object.
            data (Union[Dict, ByteString, List[Tuple], IO]):
                Dictionary, list of tuples, bytes, or file-like
                object to send in the body of the :class:`Request`.
            json (JSON): json data to send in the body of the :class:`Request`.
            **kwargs: Optional arguments that ``request`` takes.

        Returns:
            request.Response
        """
        if self.session:
            return self.session.put(url=url, data=data, json=json, **kwargs)
        return requests.put(url=url, data=data, json=json, **kwargs)

    def patch(self,
              url: str,
              data: Union[Dict, ByteString, List[Tuple], IO] = None,
              json: str = None,
              **kwargs) -> requests.Response:
        """
        Sends a PATCH request either using the provided session or the
        single session.

        Args:
            url: URL for the new :class:`Request` object.
            data (Union[Dict, ByteString, List[Tuple], IO]):
                Dictionary, list of tuples, bytes, or file-like
                object to send in the body of the :class:`Request`.
            json (JSON): json data to send in the body of the :class:`Request`.
            **kwargs: Optional arguments that ``request`` takes.

        Returns:
            request.Response
        """
        if self.session:
            return self.session.patch(url=url, data=data, json=json, **kwargs)
        return requests.patch(url=url, data=data, json=json, **kwargs)

    def delete(self, url: str, **kwargs) -> requests.Response:
        """
        Sends a DELETE request either using the provided session or the
        single session.

        Args:
            url (str): URL for the new :class:`Request` object.
            **kwargs: Optional arguments that ``request`` takes.

        Returns:
            request.Response
        """
        if self.session:
            return self.session.delete(url=url, **kwargs)
        return requests.delete(url=url, **kwargs)

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

    def close(self) -> None:
        """
        Close http session
        Returns:
            None
        """
        if self.session:
            self.session.close()
