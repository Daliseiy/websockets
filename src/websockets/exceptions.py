"""
:mod:`websockets.exceptions` defines the following exception hierarchy:

* :exc:`WebSocketException`
    * :exc:`ConnectionClosed`
        * :exc:`ConnectionClosedError`
        * :exc:`ConnectionClosedOK`
    * :exc:`InvalidHandshake`
        * :exc:`SecurityError`
        * :exc:`InvalidMessage`
        * :exc:`InvalidHeader`
            * :exc:`InvalidHeaderFormat`
            * :exc:`InvalidHeaderValue`
            * :exc:`InvalidOrigin`
            * :exc:`InvalidUpgrade`
        * :exc:`InvalidStatus`
        * :exc:`InvalidStatusCode` (legacy)
        * :exc:`NegotiationError`
            * :exc:`DuplicateParameter`
            * :exc:`InvalidParameterName`
            * :exc:`InvalidParameterValue`
        * :exc:`AbortHandshake`
        * :exc:`RedirectHandshake`
    * :exc:`InvalidState`
    * :exc:`InvalidURI`
    * :exc:`PayloadTooBig`
    * :exc:`ProtocolError`

"""

from __future__ import annotations

import http
from typing import Optional

from . import datastructures, frames, http11


__all__ = [
    "WebSocketException",
    "ConnectionClosed",
    "ConnectionClosedError",
    "ConnectionClosedOK",
    "InvalidHandshake",
    "SecurityError",
    "InvalidMessage",
    "InvalidHeader",
    "InvalidHeaderFormat",
    "InvalidHeaderValue",
    "InvalidOrigin",
    "InvalidUpgrade",
    "InvalidStatus",
    "InvalidStatusCode",
    "NegotiationError",
    "DuplicateParameter",
    "InvalidParameterName",
    "InvalidParameterValue",
    "AbortHandshake",
    "RedirectHandshake",
    "InvalidState",
    "InvalidURI",
    "PayloadTooBig",
    "ProtocolError",
    "WebSocketProtocolError",
]


class WebSocketException(Exception):
    """
    Base class for all exceptions defined by :mod:`websockets`.

    """


class ConnectionClosed(WebSocketException):
    """
    Raised when trying to interact with a closed connection.

    Provides the connection close code and reason in its ``code`` and
    ``reason`` attributes respectively.

    """

    def __init__(self, code: int, reason: str) -> None:
        self.code = code
        self.reason = reason
        super().__init__(str(frames.Close(code, reason)))


class ConnectionClosedError(ConnectionClosed):
    """
    Like :exc:`ConnectionClosed`, when the connection terminated with an error.

    This means the close code is different from 1000 (OK) and 1001 (going away).

    """

    def __init__(self, code: int, reason: str) -> None:
        assert code != 1000 and code != 1001
        super().__init__(code, reason)


class ConnectionClosedOK(ConnectionClosed):
    """
    Like :exc:`ConnectionClosed`, when the connection terminated properly.

    This means the close code is 1000 (OK) or 1001 (going away).

    """

    def __init__(self, code: int, reason: str) -> None:
        assert code == 1000 or code == 1001
        super().__init__(code, reason)


class InvalidHandshake(WebSocketException):
    """
    Raised during the handshake when the WebSocket connection fails.

    """


class SecurityError(InvalidHandshake):
    """
    Raised when a handshake request or response breaks a security rule.

    Security limits are hard coded.

    """


class InvalidMessage(InvalidHandshake):
    """
    Raised when a handshake request or response is malformed.

    """


class InvalidHeader(InvalidHandshake):
    """
    Raised when a HTTP header doesn't have a valid format or value.

    """

    def __init__(self, name: str, value: Optional[str] = None) -> None:
        self.name = name
        self.value = value
        if value is None:
            message = f"missing {name} header"
        elif value == "":
            message = f"empty {name} header"
        else:
            message = f"invalid {name} header: {value}"
        super().__init__(message)


class InvalidHeaderFormat(InvalidHeader):
    """
    Raised when a HTTP header cannot be parsed.

    The format of the header doesn't match the grammar for that header.

    """

    def __init__(self, name: str, error: str, header: str, pos: int) -> None:
        self.name = name
        error = f"{error} at {pos} in {header}"
        super().__init__(name, error)


class InvalidHeaderValue(InvalidHeader):
    """
    Raised when a HTTP header has a wrong value.

    The format of the header is correct but a value isn't acceptable.

    """


class InvalidOrigin(InvalidHeader):
    """
    Raised when the Origin header in a request isn't allowed.

    """

    def __init__(self, origin: Optional[str]) -> None:
        super().__init__("Origin", origin)


class InvalidUpgrade(InvalidHeader):
    """
    Raised when the Upgrade or Connection header isn't correct.

    """


class InvalidStatus(InvalidHandshake):
    """
    Raised when a handshake response rejects the WebSocket upgrade.

    """

    def __init__(self, response: http11.Response) -> None:
        self.response = response
        message = f"server rejected WebSocket connection: HTTP {response.status_code:d}"
        super().__init__(message)


class InvalidStatusCode(InvalidHandshake):
    """
    Raised when a handshake response status code is invalid.

    The integer status code is available in the ``status_code`` attribute and
    HTTP headers in the ``headers`` attribute.

    """

    def __init__(self, status_code: int, headers: datastructures.Headers) -> None:
        self.status_code = status_code
        self.headers = headers
        message = f"server rejected WebSocket connection: HTTP {status_code}"
        super().__init__(message)


class NegotiationError(InvalidHandshake):
    """
    Raised when negotiating an extension fails.

    """


class DuplicateParameter(NegotiationError):
    """
    Raised when a parameter name is repeated in an extension header.

    """

    def __init__(self, name: str) -> None:
        self.name = name
        message = f"duplicate parameter: {name}"
        super().__init__(message)


class InvalidParameterName(NegotiationError):
    """
    Raised when a parameter name in an extension header is invalid.

    """

    def __init__(self, name: str) -> None:
        self.name = name
        message = f"invalid parameter name: {name}"
        super().__init__(message)


class InvalidParameterValue(NegotiationError):
    """
    Raised when a parameter value in an extension header is invalid.

    """

    def __init__(self, name: str, value: Optional[str]) -> None:
        self.name = name
        self.value = value
        if value is None:
            message = f"missing value for parameter {name}"
        elif value == "":
            message = f"empty value for parameter {name}"
        else:
            message = f"invalid value for parameter {name}: {value}"
        super().__init__(message)


class AbortHandshake(InvalidHandshake):
    """
    Raised to abort the handshake on purpose and return a HTTP response.

    This exception is an implementation detail.

    The public API is :meth:`~legacy.server.WebSocketServerProtocol.process_request`.

    """

    def __init__(
        self,
        status: http.HTTPStatus,
        headers: datastructures.HeadersLike,
        body: bytes = b"",
    ) -> None:
        self.status = status
        self.headers = datastructures.Headers(headers)
        self.body = body
        message = f"HTTP {status:d}, {len(self.headers)} headers, {len(body)} bytes"
        super().__init__(message)


class RedirectHandshake(InvalidHandshake):
    """
    Raised when a handshake gets redirected.

    This exception is an implementation detail.

    """

    def __init__(self, uri: str) -> None:
        self.uri = uri

    def __str__(self) -> str:
        return f"redirect to {self.uri}"


class InvalidState(WebSocketException, AssertionError):
    """
    Raised when an operation is forbidden in the current state.

    This exception is an implementation detail.

    It should never be raised in normal circumstances.

    """


class InvalidURI(WebSocketException):
    """
    Raised when connecting to an URI that isn't a valid WebSocket URI.

    """

    def __init__(self, uri: str) -> None:
        self.uri = uri
        message = "{} isn't a valid URI".format(uri)
        super().__init__(message)


class PayloadTooBig(WebSocketException):
    """
    Raised when receiving a frame with a payload exceeding the maximum size.

    """


class ProtocolError(WebSocketException):
    """
    Raised when a frame breaks the protocol.

    """


WebSocketProtocolError = ProtocolError  # for backwards compatibility
