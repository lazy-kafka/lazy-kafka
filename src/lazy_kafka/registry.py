"""Confluent kafka registry interface (API).

`confluent_kafka` uses requests library, which is not going to cut it for us.


textual docs: https://textual.textualize.io/guide/workers/#thread-workers
"""
from __future__ import annotations
import httpx
from functools import partialmethod

list_schemas = "schemas/types"

class ScheamRegistry:
    DEFAULT_HOST = "http://localhost:8081/"

    def __init__(self, host: str = DEFAULT_HOST) -> None:
        self.host = host

    def _generic_get_json(self, url: str):
        response = httpx.get(self.host + url)
        return response.json()

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

def list():
    sr = ScheamRegistry()
    return sr.subjects()

if __name__ == "__main__":
    sr = ScheamRegistry()
    from rich.pretty import pprint
    pprint(sr.subjects())
