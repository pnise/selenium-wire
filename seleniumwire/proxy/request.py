"""Houses the classes used to transfer request and response data between components. """
from typing import Dict, List, Union
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

from .utils import CaseInsensitiveDict


class Request:
    """Represents an HTTP request."""

    def __init__(self, *,
                 method: str,
                 url: str,
                 headers: Dict[str, str],
                 body: bytes = b''):
        """Initialise a new Request object.

        Args:
            method: The request method - GET, POST etc.
            url: The request URL.
            headers: The request headers as a dictionary.
            body: The request body as bytes.
        """
        self.id = None  # The id is set for captured requests
        self.method = method
        self.url = url
        # XXX: this is not fully RFC7230 compliant. Headers with the
        # same name will be lost when converting to a dictionary.
        self.headers = CaseInsensitiveDict(headers)
        self.body = body
        self.response = None

    @property
    def body(self) -> bytes:
        """Get the request body.

        Returns: The request body as bytes.
        """
        return self._body

    @body.setter
    def body(self, b: bytes):
        if b is None:
            self._body = b''
        elif isinstance(b, str):
            self._body = b.encode('utf-8')
        elif not isinstance(b, bytes):
            raise TypeError('body must be of type bytes')
        else:
            self._body = b

    @property
    def querystring(self) -> str:
        """Get the query string from the request.

        Returns: The query string.
        """
        return urlsplit(self.url).query

    @querystring.setter
    def querystring(self, qs: str):
        parts = list(urlsplit(self.url))
        parts[3] = qs
        self.url = urlunsplit(parts)

    @property
    def params(self) -> Dict[str, Union[str, List[str]]]:
        """Get the request parameters.

        Parameters are returned as a dictionary. Each dictionary entry will have a single
        string value, unless a parameter happens to occur more than once in the request,
        in which case the value will be a list of strings.

        Returns: A dictionary of request parameters.
        """
        qs = self.querystring

        if self.headers.get('Content-Type') == 'application/x-www-form-urlencoded' and self.body:
            qs = self.body.decode('utf-8', errors='replace')

        return {name: val[0] if len(val) == 1 else val
                for name, val in parse_qs(qs, keep_blank_values=True).items()}

    @params.setter
    def params(self, p: Dict[str, Union[str, List[str]]]):
        qs = urlencode(p, doseq=True)

        if self.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
            self.body = qs.encode('utf-8', errors='replace')
        else:
            parts = list(urlsplit(self.url))
            parts[3] = qs
            self.url = urlunsplit(parts)

    @property
    def path(self) -> str:
        """Get the request path.

        Returns: The request path.
        """
        return urlsplit(self.url).path

    @path.setter
    def path(self, p: str):
        parts = list(urlsplit(self.url))
        parts[2] = p
        self.url = urlunsplit(parts)

    def __repr__(self):
        return 'Request(method={method!r}, url={url!r}, headers={headers!r}, body={_body!r})' \
            .format_map(vars(self))

    def __str__(self):
        return self.url


class Response:
    """Represents an HTTP response."""

    def __init__(self, *,
                 status_code: int,
                 reason: str,
                 headers: Dict[str, str],
                 body: bytes = b''):
        """Initialise a new Response object.

        Args:
            status_code: The status code.
            reason: The reason message (e.g. "OK" or "Not Found").
            headers: The response headers as a dictionary.
            body: The response body as bytes.
        """
        self.status_code = status_code
        self.reason = reason
        self.headers = CaseInsensitiveDict(headers)
        self.body = body

    @property
    def body(self) -> bytes:
        """Get the response body.

        Returns: The response body as bytes.
        """
        return self._body

    @body.setter
    def body(self, b: bytes):
        if b is None:
            self._body = b''
        elif isinstance(b, str):
            self._body = b.encode('utf-8')
        elif not isinstance(b, bytes):
            raise TypeError('body must be of type bytes')
        else:
            self._body = b

    def __repr__(self):
        return 'Response(status_code={status_code!r}, reason={reason!r}, headers={headers!r}, ' \
               'body={_body!r})'.format_map(vars(self))

    def __str__(self):
        return '{} {}'.format(self.status_code, self.reason)