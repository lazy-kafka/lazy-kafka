"""Confluent kafka registry interface (API).

`confluent_kafka` uses requests library, which is not going to cut it for us.


textual docs: https://textual.textualize.io/guide/workers/#thread-workers


This is confulent cloud, so not that relevant
Schemas API: https://docs.confluent.io/cloud/current/api.html#tag/Modes-(v1)/operation/updateTopLevelMode

"""

from __future__ import annotations
import logging
from typing import Any, Optional, TypedDict
import httpx
from enum import StrEnum, auto
from functools import partialmethod
import json

_LOGGER = logging.getLogger(__name__)

Subject = str
list_schemas = "schemas/types"


class SubjectDetails(TypedDict):
    id: int
    subject: Subject
    version: int
    schema: Any


class SubjectNew(TypedDict):
    """New subject.

    schema – The schema string
    schemaType – Defines the schema format: AVRO (default), PROTOBUF, JSON (Optional)
    references – Specifies the names of referenced schemas (Optional). To learn more, see Schema references.
    metadata – Specifies the metadata for the schema (Optional). To learn more, see “Metadata Properties” in Data Contracts for Schema Registry .
    ruleSet – Specifies the ruleSet for the schema (Optional). To learn more, see “Rules” in Data Contracts for Schema Registry .
    """

    schema: str
    schemaType: str
    references: Optional[Any]
    metadata: Optional[Any]
    ruleSet: Optional[Any]


class SchemaRegistryAPI(StrEnum):
    SUBJECTS = auto()
    SCHEMAS = auto()

class SchemaTypes(StrEnum):
    JSON = auto()
    PROTOBUF = auto()
    AVRO = auto()

class SchemaRegistry:
    DEFAULT_HOST = "http://localhost:8081/"
    # Reference: https://docs.confluent.io/platform/current/schema-registry/develop/api.html#content-types
    _CONTENT_TYPE = "application/vnd.schemaregistry.v1+json"

    def __init__(self, host: str = DEFAULT_HOST) -> None:
        self.host = host
        self._client = httpx.AsyncClient(
            base_url=SchemaRegistry.DEFAULT_HOST,
            headers={"Content-Type": SchemaRegistry._CONTENT_TYPE},
        )

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

    asubjects = partialmethod(_ageneric_get_json, SchemaRegistryAPI.SUBJECTS)
    subjects = partialmethod(_generic_get_json, SchemaRegistryAPI.SUBJECTS)
    subjects.__doc__ = """List subjects.

        The subjects resource provides a list of all registered subjects across 
        all contexts in your Schema Registry. A subject refers to the name under 
        which the schema is registered. If you are using Schema Registry for Kafka
        , then a subject refers to either a “<topic>-value” or “<topic>-key” 
        depending on whether you are registering the value schema for that topic 
        or the key schema. To learn more about subject name strategies, see 
        [How the naming strategies work](https://docs.confluent.io/platform/current/schema-registry/fundamentals/serdes-develop/index.html#sr-schemas-subject-name-strategies-work).
        """

    async def asubject_versions(self, subject: Subject):
        """Get all versions of `subject`."""
        _url = SchemaRegistryAPI.SUBJECTS + f"/{subject}/versions"
        return await self._ageneric_get_json(_url)

    async def asubject_latest(self, subject: Subject) -> SubjectDetails:
        """Get latest version of subject."""
        _url = SchemaRegistryAPI.SUBJECTS + f"/{subject}/versions/-1"
        return await self._ageneric_get_json(_url)

    async def asubjects_delete(self, subject: Subject, version: int):
        return await self._client.delete(url=f"subjects/{subject}/versions/{version}")
        
    async def aschema_versions(self, subject: Subject):
        _url = SchemaRegistryAPI.SUBJECTS + f"/{subject}/versions"
        return await self._ageneric_get_json(_url)

    async def asubjects_create(self, subject: Subject, data: SubjectNew):
        _url = SchemaRegistryAPI.SUBJECTS + "/" + subject + "/versions"
        print(_url)
        async with httpx.AsyncClient(
            base_url=SchemaRegistry.DEFAULT_HOST,
            headers={"Content-Type": SchemaRegistry._CONTENT_TYPE},
        ) as client:
            response = await client.post(_url, data=data)
            return response


    def _serialize_json_schema(self, schema: object) -> str:
        return json.dumps(schema)

async def test_async_api():
    import json

    sr = SchemaRegistry()
    schema = json.dumps(
        {
            "type": "object",
            "properties": {"amount": {"type": "number"}, "id": {"type": "number"}},
        }
    )
    data = SubjectNew(
        schema=schema,
        schemaType="JSONSchema",
    )
    res = await sr.asubjects_create(
        "other", data=json.dumps({"schema": schema, "schemaType": "JSON"})
    )
    print(res)


if __name__ == "__main__":
    # sr = SchemaRegistry()
    # from rich.pretty import pprint
    # pprint(sr.subjects())
    import asyncio
    # Create a nice information summary:
    # number of subjects
    # Allowed formats /schemas/types/
    # Compatibility mode (/cont
    # global mode?

    asyncio.run(test_async_api())
# >>> t = {"type": "string"}
# >>> s2 = json.dumps({"schemaType":"JSON", "schema": json.dumps(t) })
# >>> r = httpx.post("http://localhost:8081/subjects/kakadu/versions",headers={"Content-Type": "application/vnd.schemaregistry.v1+json"} ,data=s2)
