"""Confluent kafka connect interface."""
# TODO plug this to httpx
from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from requests import delete, get, post, put  # noqa
from requests.exceptions import ConnectionError, HTTPError


class HTTPMethod(Enum):
    """HTTP methods allowed."""

    GET = "get"
    PUT = "put"
    POST = "post"
    DELETE = "delete"

__all__ = ["list", "status"]

@dataclass
class ConnectorData:
    name: Optional[str] = None
    status: Optional[object] = None

class Connect:
    """Kafka Connect API helper class.

    Parameters
    ----------
    connect_url : `str`
    Kafka Connect URL
    """

    _header = {"Content-Type": "application/json"}

    def __init__(self, connect_url: str) -> None:
        self._connect_url = connect_url

    def _request(
        self, method: HTTPMethod, uri: str, data: Optional[str] = None
    ) -> str:
        """Make HTTP requests.

        Parameters
        ----------
        method: `HTTPMethod`
            HTTP method as defined in the HTTPMethod class.
        uri : `str`
            The resource identifier.
        data : `str`
            The message body for the PUT request.

        Returns
        -------
        content: `ContenT` or `None`
            The response content. Returns `None` if the request was not
            successful or if the response is empty.
        """
        if method.name in ("GET", "DELETE"):
            if data:
                raise ValueError(
                    f"data argument must be None with {method.name} method."
                )
        func = eval(method.value)
        response = None
        try:
            if data:
                response = func(uri, data=data, headers=Connect._header)
            else:
                response = func(uri)
            response.raise_for_status()
        except HTTPError as err:
            if err.response is None:
                raise ValueError("No response from the server.")
            if err.response.status_code == 404:
                message = f"Resource {uri} not found."
                return message
            # returns 409 (Conflict) if kafka cluster rebalance is in process.
            if err.response.status_code == 409:
                message = "Kafka cluster rebalance is in process."
                return message
        except ConnectionError:
            message = (
                f"Failed to establish connection with the "
                f"Connect API {self._connect_url}."
            )
            return message
        content = ""
        if response is None:
            raise ValueError("No response from the server.")
        if response.text:
            content = json.dumps(response.json(), indent=4, sort_keys=True)
        return content

    def list(self) -> dict[str,str]:
        """Get a list of active connectors."""
        uri = f"{self._connect_url}/connectors?expand=status"
        response = self._request(method=HTTPMethod.GET, uri=uri)
        content = json.loads(response)
        return  content


def list() -> list[ConnectorData]:
    """List all connectors."""
    # todo: this is just a joke, it will be rewritten
    con = Connect("http://localhost:8083")
    con_list = [ConnectorData(name=k, status=v) for k,v in con.list().items()]
    return con_list

def status():
    """Get status of connector."""
    pass

if __name__ == "__main__":
    con = Connect("http://localhost:8083")
    from rich.pretty import pprint
    pprint(con.list())
    pprint(list())
