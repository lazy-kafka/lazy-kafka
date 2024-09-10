"""Confluent kafka connect interface."""

# TODO plug this to httpx
from __future__ import annotations

from functools import partialmethod
from typing import Any, Self
import json
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional
import logging
from requests import delete, get, post, put  # noqa
from requests.exceptions import ConnectionError, HTTPError

import httpx

_LOGGER = logging.getLogger(__name__)


class HTTPMethod(Enum):
    """HTTP methods allowed."""

    GET = "get"
    PUT = "put"
    POST = "post"
    DELETE = "delete"


__all__ = ["list", "status"]


@dataclass(frozen=True, slots=False)
class ConnectorData:
    name: Optional[str] = None
    state: Optional[str] = None
    worker_id: Optional[str] = None
    type: Optional[str] = None

    def to_dict(self: Self) -> dict[str, Any]:
        """Return contents as dict"""
        return asdict(self)

    def to_tuple(self: Self) -> tuple[str, str, str, str]:
        return tuple(self.to_dict().values())

class NeoConnect:
    DEFAULT_HOST = "http://localhost:8083/"
    # [Reference](https://docs.confluent.io/platform/current/connect/references/restapi.html#content-types)
    _CONTENT_TYPE = "application/json"

    def __init__(self, host: str = DEFAULT_HOST) -> None:
        self.host = host

    def __repr__(self):
        return f"Connect@{self.host}"

    def _generic_get_json(self, url: str):
        response = httpx.get(self.host + url)
        return response.json()

    async def _ageneric_get_json(self, url: str):
         _LOGGER.debug("%s request: %s", self, url)
         async with httpx.AsyncClient() as client:
            response = await client.get(self.host + url)
            return response.json()
    ainfo = partialmethod(_ageneric_get_json, "")
    ainfo.__doc__ = """Connect Cluster information.

    Top-level (root) request that gets the version of the Connect worker that
    serves the REST request, the git commit ID of the source code, and the
    Kafka cluster ID that the worker is connected to.
    """

    alist = partialmethod(_ageneric_get_json, "connectors?expand=status")
    alist.__doc__ = """Get a list of active connectiors.
    
    [Reference](https://docs.confluent.io/platform/current/connect/references/restapi.html#connectors)
    """
    #TODO: Post connector [Ref](https://docs.confluent.io/platform/current/connect/references/restapi.html#post--connectors)
    #TODO: Put Connector - update config
    #TODO: Post restart
    #TODO: Get connector info [Ref](https://docs.confluent.io/platform/current/connect/references/restapi.html#get--connectors-(string-name))
   # TODO:  connector config info [Ref](https://docs.confluent.io/platform/current/connect/references/restapi.html#get--connectors-(string-name)-config)

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

    def _request(self, method: HTTPMethod, uri: str, data: Optional[str] = None) -> str:
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

    def list(self) -> dict[str, Any]:
        """Get a list of active connectors."""
        uri = f"{self._connect_url}/connectors?expand=status"
        response = self._request(method=HTTPMethod.GET, uri=uri)
        content = json.loads(response)
        return content


def list():
    """List all connectors."""
    # todo: this is just a joke, it will be rewritten
    con = Connect("http://localhost:8083")
    cc = con.list()
    _LOGGER.debug(json.dumps(cc, indent=2, sort_keys=True))
    con_list = {
        k: ConnectorData(
            name=k,
            state=v["status"]["connector"]["state"],
            worker_id=v["status"]["connector"]["worker_id"],
            type=v["status"]["type"],
        )
        for k, v in con.list().items()
    }
    return con_list


def status():
    """Get status of connector."""
    pass


if __name__ == "__main__":
    con = Connect("http://localhost:8083")
    from rich.pretty import pprint

    pprint(con.list())
    pprint(list())
