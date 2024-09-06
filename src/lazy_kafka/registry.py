"""Confluent kafka registry interface (API).

`confluent_kafka` uses requests library, which is not going to cut it for us.


textual docs: https://textual.textualize.io/guide/workers/#thread-workers


This is confulent cloud, so not that relevant
Schemas API: https://docs.confluent.io/cloud/current/api.html#tag/Modes-(v1)/operation/updateTopLevelMode

"""
from __future__ import annotations
import logging
import httpx
from functools import partialmethod

_LOGGER = logging.getLogger(__name__)

list_schemas = "schemas/types"


class SchemaRegistry:
    DEFAULT_HOST = "http://localhost:8081/"
    # Reference: https://docs.confluent.io/platform/current/schema-registry/develop/api.html#content-types
    _CONTENT_TYPE = "application/vnd.schemaregistry.v1+json"

    def __init__(self, host: str = DEFAULT_HOST) -> None:
        self.host = host

    def __repr__(self):
        return f"SchemaRegistry@{self.host}"

    def _generic_get_json(self, url: str):
        response = httpx.get(self.host + url)
        return response.json()

    async def _ageneric_get_json(self, url: str):
         _LOGGER.debug("%s request: %s", self, url)
         async with httpx.AsyncClient() as client:
            response = await client.get(self.host + url)
            return response.json()

    asubjects = partialmethod(_ageneric_get_json, "subjects")
    subjects = partialmethod(_generic_get_json, "subjects")
    subjects.__doc__ = """List subjects.

        The subjects resource provides a list of all registered subjects across 
        all contexts in your Schema Registry. A subject refers to the name under 
        which the schema is registered. If you are using Schema Registry for Kafka
        , then a subject refers to either a “<topic>-value” or “<topic>-key” 
        depending on whether you are registering the value schema for that topic 
        or the key schema. To learn more about subject name strategies, see 
        [How the naming strategies work](https://docs.confluent.io/platform/current/schema-registry/fundamentals/serdes-develop/index.html#sr-schemas-subject-name-strategies-work).
        """



if __name__ == "__main__":
    sr = SchemaRegistry()
    from rich.pretty import pprint
    pprint(sr.subjects())
    # Create a nice information summary:
    # number of subjects
    # Allowed formats /schemas/types/
    # Compatibility mode (/cont
    # global mode?
