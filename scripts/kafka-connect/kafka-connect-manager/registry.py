from pathlib import Path
import json
from types import NotImplementedType

from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry import Schema
from lib import SCHEMA_REGISTRY_URL, TOPIC, SerializationType, cli


def get_schema(path: Path = Path("./test.avsc")):
    with open(path, "r", encoding="utf-8") as f:
        schema_str = f.read()
    return schema_str

def register_schema(schema_registry_url: str, schema_registry_subject: str, schema_str: str, schema_type: SerializationType, *, schema_registry_api_key:str="IVW44Y6DYGNXUSOY", schema_registry_api_secret: str="FAAs4uKLZI4z6nuhZSvoCBzH2uN2pC+LecSna0zMtt563aab6OBYv+uI2hD/qc/k"):
    sr = SchemaRegistryClient({"url": schema_registry_url, "basic.auth.user.info":f"{schema_registry_api_key}:{schema_registry_api_secret}"})
    schema = Schema(schema_str, schema_type=schema_type.value)
    schema_id = sr.register_schema(
        subject_name=schema_registry_subject, schema=schema
    )
    return schema_id

if __name__ == "__main__":
    # for the dummy testing (create_messages.py) use the default val
    # for the ropax_avro we use this:
    # for avro
    # for json
    schema_type, dummy_mode = cli()
    
    match (schema_type, dummy_mode):
        case (SerializationType.JSON, True):
            schema = get_schema(Path('./dummy-json-schema.json'))
        case (SerializationType.JSON, False):
            schema = get_schema(Path('./ropax-avro-schema.json'))
        case (SerializationType.AVRO, False):
            schema = get_schema(Path('./avro_schema.avsc'))
        case _:
            raise NotImplementedError

    #res = register_schema_avro(SCHEMA_REGISTRY_URL, TOPIC + "-value", schema, schema_type)
    res = register_schema(SCHEMA_REGISTRY_URL, TOPIC + "-value" , schema, schema_type)
    print(f"{res!r}")
