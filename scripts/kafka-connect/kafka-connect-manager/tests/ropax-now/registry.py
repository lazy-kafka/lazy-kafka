from pathlib import Path
import json

from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry import Schema

# imort from constants


def get_schema(path: Path = Path("./test.avsc")):
    with open(path, "r", encoding="utf-8") as f:
        schema_str = f.read()
    return schema_str
    return json.dumps(schema_str)



def register_schema(schema_registry_url: str, schema_registry_subject: str, schema_str: str):
    sr = SchemaRegistryClient({"url": schema_registry_url})
    schema = Schema(schema_str, schema_type="AVRO")
    schema_id = sr.register_schema(
        subject_name=schema_registry_subject, schema=schema
    )
    return schema_id


SCHEMA_REGISTRY_URL = "http://localhost:8081"
TOPIC = "foo"

if __name__ == "__main__":
    # for the dummy testing (create_messages.py) use the default val
    # for the ropax_avro we use this:
    schema = get_schema(Path('./avro_schema.avsc'))
    res = register_schema(SCHEMA_REGISTRY_URL, TOPIC + "-value", schema)
    print(f"{res!r}")
