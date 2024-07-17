"""
Base http client module
"""
import logging
from pydantic import AnyHttpUrl
from typing import Dict, ByteString, List, IO, Tuple, Union
import requests

from filip.models.base import FiwareHeader
from filip.utils import validate_http_url


class BaseHttpClient:
    """
    Base client for all derived api-clients.

    Args:
        session: request session object. This is required for reusing
            the same connection
        reuse_session (bool):
        fiware_header: Fiware header object required for multi tenancy
        **kwargs: Optional arguments that ``request`` takes.

    """
    def __init__(self,
                 url: Union[AnyHttpUrl, str] = None,
                 *,
                 session: requests.Session = None,
                 fiware_header: Union[Dict, FiwareHeader] = None,
                 **kwargs):

        self.logger = logging.getLogger(
            name=f"{self.__class__.__name__}")
        self.logger.addHandler(logging.NullHandler())
        self.logger.debug("Creating %s", self.__class__.__name__)

        if url:
            self.logger.debug("Checking url style...")
            self.base_url = validate_http_url(url)

        if session:
            self.session = session
            self._external_session = True
        else:
            self.session = None
            self._headers = {}

        if not fiware_header:
            self.fiware_headers = FiwareHeader()
        else:
            self.fiware_headers = fiware_header

        self.headers.update(kwargs.pop('headers', {}))
        self.kwargs: Dict = kwargs

    # Context Manager Protocol
    def __enter__(self):
        if not self.session:
            self.session = requests.Session()
            self.headers.update(self.fiware_headers.model_dump(by_alias=True))
            self._external_session = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def fiware_headers(self) -> FiwareHeader:
        """
        Get fiware header

        Returns:
            FiwareHeader
        """
        return self._fiware_headers

    @fiware_headers.setter
    def fiware_headers(self, headers: Union[Dict, FiwareHeader]) -> None:
        """
        Sets new fiware header

        Args:
            headers (Dict, FiwareHeader): New headers either as FiwareHeader
                object or as dict.

        Example:
            {fiware-service: "MyService",
             fiware-servicepath: "/MyServicePath"}

        Returns:
            None
        """
        if isinstance(headers, FiwareHeader):
            self._fiware_headers = headers
        elif isinstance(headers, dict):
            self._fiware_headers = FiwareHeader.model_validate(headers)
        elif isinstance(headers, str):
            self._fiware_headers = FiwareHeader.model_validate_json(headers)
        else:
            raise TypeError(f'Invalid headers! {type(headers)}')
        self.headers.update(self.fiware_headers.model_dump(by_alias=True))

    @property
    def fiware_service(self) -> str:
        """
        Get current fiware service
        Returns:
            str
        """
        return self.fiware_headers.service

    @fiware_service.setter
    def fiware_service(self, service: str) -> None:
        """
        Set new fiware service
        Args:
            service:

        Returns:
            None
        """
        self._fiware_headers.service = service
        self.headers.update(self.fiware_headers.model_dump(by_alias=True))

    @property
    def fiware_service_path(self) -> str:
        """
        Get current fiware service path
        Returns:
            str
        """
        return self.fiware_headers.service_path

    @fiware_service_path.setter
    def fiware_service_path(self, service_path: str) -> None:
        """
        Set new fiware service path
        Args:
            service_path (str): New fiware service path. Must start with '/'

        Returns:
            None
        """
        self._fiware_headers.service_path = service_path
        self.headers.update(self.fiware_headers.model_dump(by_alias=True))

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
    def get(self,
            url: str,
            params: Union[Dict, List[Tuple], ByteString] = None,
            **kwargs) -> requests.Response:
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

        kwargs.update({k: v for k, v in self.kwargs.items()
                       if k not in kwargs.keys()})

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
        kwargs.update({k: v for k, v in self.kwargs.items()
                       if k not in kwargs.keys()})

        if self.session:
            return self.session.options(url=url, **kwargs)
        return requests.options(url=url, **kwargs)

    def head(self, url: str,
             params: Union[Dict, List[Tuple], ByteString] = None,
             **kwargs) -> requests.Response:
        """
        Sends a HEAD request either using the provided session or the
        single session.

        Args:
            url (str): URL for the new :class:`Request` object.
            params (optional): Dictionary, list of tuples or bytes
                to send in the query string for the :class:`Request`.
            **kwargs: Optional arguments that ``request`` takes.

        Returns:
            requests.Response
        """
        kwargs.update({k: v for k, v in self.kwargs.items()
                       if k not in kwargs.keys()})

        if self.session:
            return self.session.head(url=url, params=params, **kwargs)
        return requests.head(url=url, params=params, **kwargs)

    def post(self,
             url: str,
             data: Union[Dict, ByteString, List[Tuple], IO, str] = None,
             json: Dict = None,
             **kwargs) -> requests.Response:
        """
        Sends a POST request either using the provided session or the
        single session.

        Args:
            url: URL for the new :class:`Request` object.
            data: Dictionary, list of tuples, bytes, or file-like object to
                send in the body of the :class:`Request`.
            json: A JSON serializable Python object to send in the
                body of the :class:`Request`.
            **kwargs: Optional arguments that ``request`` takes.

        Returns:

        """
        kwargs.update({k: v for k, v in self.kwargs.items()
                       if k not in kwargs.keys()})

        if self.session:
            return self.session.post(url=url, data=data, json=json, **kwargs)
        return requests.post(url=url, data=data, json=json, **kwargs)

    def put(self,
            url: str,
            data: Union[Dict, ByteString, List[Tuple], IO, str] = None,
            json: Dict = None,
            **kwargs) -> requests.Response:
        """
        Sends a PUT request either using the provided session or the
        single session.

        Args:
            url: URL for the new :class:`Request` object.
            data (Union[Dict, ByteString, List[Tuple], IO]):
                Dictionary, list of tuples, bytes, or file-like
                object to send in the body of the :class:`Request`.
            json (Dict): A JSON serializable Python object to send in the
                body of the :class:`Request`..
            **kwargs: Optional arguments that ``request`` takes.

        Returns:
            request.Response
        """
        kwargs.update({k: v for k, v in self.kwargs.items()
                       if k not in kwargs.keys()})

        if self.session:
            return self.session.put(url=url, data=data, json=json, **kwargs)
        return requests.put(url=url, data=data, json=json, **kwargs)

    def patch(self,
              url: str,
              data: Union[Dict, ByteString, List[Tuple], IO, str] = None,
              json: Dict = None,
              **kwargs) -> requests.Response:
        """
        Sends a PATCH request either using the provided session or the
        single session.

        Args:
            url: URL for the new :class:`Request` object.
            data (Union[Dict, ByteString, List[Tuple], IO]):
                Dictionary, list of tuples, bytes, or file-like
                object to send in the body of the :class:`Request`.
            json (Dict): A JSON serializable Python object to send in the
                body of the :class:`Request`..
            **kwargs: Optional arguments that ``request`` takes.

        Returns:
            request.Response
        """
        kwargs.update({k: v for k, v in self.kwargs.items()
                       if k not in kwargs.keys()})

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
        kwargs.update({k: v for k, v in self.kwargs.items()
                       if k not in kwargs.keys()})

        if self.session:
            return self.session.delete(url=url, **kwargs)
        return requests.delete(url=url, **kwargs)

    def log_error(self,
                  err: requests.RequestException,
                  msg: str = None) -> None:
        """
        Outputs the error messages from the client request function. If
        additional information is available in the server response this will
        be forwarded to the logging output.

        Note:
            The user is responsible to setup the logging system

        Args:
            err: Request Error
            msg: error message from calling function

        Returns:
            None
        """
        if err.response is not None:
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
        if self.session and not self._external_session:
            self.session.close()
