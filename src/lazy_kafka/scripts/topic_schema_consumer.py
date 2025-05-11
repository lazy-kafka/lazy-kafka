from __future__ import annotations

from confluent_kafka import OFFSET_END, Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONDeserializer

from lazy_kafka.config import Configuration

TOPIC = "user-topic"

def dict_to_user(obj, ctx):
    """
    Converts object literal(dict) to a User instance.

    Args:
        ctx (SerializationContext): Metadata pertaining to the serialization
            operation.
        obj (dict): Object literal(dict)
    """
    if obj is None:
        return None

    return obj

def main():
    cfg = Configuration()

    schema_registry_conf = {
        "url": cfg.registry.host,
    }
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    _deserializer = JSONDeserializer(
        schema_str=f"{TOPIC}-value",
        from_dict=dict_to_user,
        schema_registry_client=schema_registry_client,
    )
    settings = {
        "bootstrap.servers": cfg.kafka.bootstrap_server,
        "group.id": "my-work-group",
        "auto.offset.reset": "latest",
    }

    def on_assign(consumer, partitions):
        for partition in partitions:
            partition.offset = OFFSET_END
        consumer.assign(partitions)

    consumer = Consumer(settings)

    consumer.subscribe([TOPIC], on_assign=on_assign)

    msg = consumer.poll(1.0)
    print(msg)


if __name__ == "__main__":
    main()
