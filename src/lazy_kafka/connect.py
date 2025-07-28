"""Confluent kafka connect interface."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from functools import partialmethod
from typing import TYPE_CHECKING, Any, Self

import httpx

from lazy_kafka.config import ConnectConfiguration

if TYPE_CHECKING:
    from collections.abc import Coroutine

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=False)
class ConnectorData:
    """Connector Data.

    Basic representation of returned data.

    Attributes:
        name:
        state:
        worker_id:
        type:
    """

    name: str | None = None
    state: str | None = None  # TODO: enum RUNNING | FAILED
    worker_id: str | None = None
    type: str | None = None

    def __iter__(self: Self) -> Iterable[str | None]:
        return iter(self.__dict__.values())

    def to_dict(self: Self) -> dict[str, Any]:
        """Return contents as dict."""
        return asdict(self)

    def to_tuple(self: Self) -> tuple[str, str, str, str]:
        return tuple(self.to_dict().values())

    def to_table_values(self):
        return self.to_dict().values()

    @staticmethod
    def from_response(response: dict[str, Any]) -> dict[str, ConnectorData]:
        _LOGGER.debug("%s", response)
        return {
            k: ConnectorData(
                name=k,
                state=v["status"]["connector"]["state"],
                worker_id=v["status"]["connector"]["worker_id"],
                type=v["status"]["type"],
            )
            for k, v in response.items()
        }


class Connect:
    # [Reference](https://docs.confluent.io/platform/current/connect/references/restapi.html#content-types)
    _CONTENT_TYPE = "application/json"

    def __init__(self, config: ConnectConfiguration = ConnectConfiguration()) -> None:
        """Initialise client.

        Performs a sanity 'get' request, before creating a client.

        Args:
            host:
        """
        _auth = None
        if config.username and config.password:
            # Basic authentication
            _auth = httpx.BasicAuth(username=config.username, password=config.password)

        try:
            _debug_info = httpx.get(config.host, auth=_auth)
        except httpx.HTTPError as e:
            _LOGGER.error("Connection error: %s", e)
            raise ConnectionRefusedError(f"Cannot connect to {config.host}") from e
        _LOGGER.debug("Service info: %s", _debug_info)
        assert _debug_info.status_code == 200
        self.host = config.host
        self._client = httpx.AsyncClient(
            base_url=self.host,
            headers={"Content-Type": Connect._CONTENT_TYPE},
            auth=_auth,
        )

    def __repr__(self):
        return f"Connect@{self.host}"

    def _generic_get_json(self, url: str):
        response = httpx.get(self.host + url)
        return response.json()

    async def _ageneric_get_json(self, url: str) -> dict[str, Any]:
        _LOGGER.debug("%s request: %s", self, url)
        async with httpx.AsyncClient() as client:
            response = await client.get(self.host + url)
            return response.json()

    ainfo = partialmethod(_ageneric_get_json, "/")
    ainfo.__doc__ = """Connect Cluster information.

    Top-level (root) request that gets the version of the Connect worker that
    serves the REST request, the git commit ID of the source code, and the
    Kafka cluster ID that the worker is connected to.
    """

    alist: partialmethod[Coroutine[Any, Any, dict[str, ConnectorData]]] = partialmethod(
        _ageneric_get_json, "/connectors?expand=status"
    )
    alist.__doc__ = """Get a list of active connectiors.

    [Reference](https://docs.confluent.io/platform/current/connect/references/restapi.html#connectors)
    """

    async def aget_details(self, connector_id: ConnectorData):
        # todo get connector details
        _LOGGER.debug(f"{connector_id=}")
        return connector_id.to_dict()

    asubjects = alist

    # TODO: Post connector [Ref](https://docs.confluent.io/platform/current/connect/references/restapi.html#post--connectors)
    # TODO: Put Connector - update config
    # TODO: Post restart
    # TODO: Get connector info [Ref](https://docs.confluent.io/platform/current/connect/references/restapi.html#get--connectors-(string-name))


# TODO:  connector config info [Ref](https://docs.confluent.io/platform/current/connect/references/restapi.html#get--connectors-(string-name)-config)


async def test_async_api():
    from rich.pretty import pprint

    reg = Connect()
    connectors = await reg.alist()
    pprint(connectors)


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_async_api())
