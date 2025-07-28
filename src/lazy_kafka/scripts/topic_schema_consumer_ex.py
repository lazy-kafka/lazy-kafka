from __future__ import annotations

from confluent_kafka import Consumer
from confluent_kafka.schema_registry.json_schema import JSONDeserializer

from lazy_kafka.config import Configuration

TOPIC = "user-topic"

from confluent_kafka.serialization import MessageField, SerializationContext


class User:
    """
    User record.

    Args:
        name (str): User's name
        favorite_number (int): User's favorite number
        favorite_color (str): User's favorite color
    """

    def __init__(self, name=None, favorite_number=None, favorite_color=None):
        self.name = name
        self.favorite_number = favorite_number
        self.favorite_color = favorite_color


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

    return User(
        name=obj["name"],
        favorite_number=obj["favorite_number"],
        favorite_color=obj["favorite_color"],
    )


def main():
    cfg = Configuration()

    settings = {
        "bootstrap.servers": cfg.kafka.bootstrap_servers,
        "group.id": "my-work-group-testicle",
        "auto.offset.reset": "latest",
        "security.protocol": "plaintext",
    }

    schema_str = """
    {
      "$schema": "http://json-schema.org/draft-07/schema#",
      "title": "User",
      "description": "A Confluent Kafka Python User",
      "type": "object",
      "properties": {
        "name": {
          "description": "User's name",
          "type": "string"
        },
        "favorite_number": {
          "description": "User's favorite number",
          "type": "number",
          "exclusiveMinimum": 0
        },
        "favorite_color": {
          "description": "User's favorite color",
          "type": "string"
        }
      },
      "required": [ "name", "favorite_number", "favorite_color" ]
    }
    """
    JSONDeserializer(schema_str, from_dict=dict_to_user)

    consumer = Consumer(settings)
    consumer.subscribe([TOPIC])

    while True:
        try:
            # SIGINT can't be handled when polling, limit timeout to 1 second.
            msg = consumer.poll(1.0)
            if msg is None:
                continue

            print(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE))
        except KeyboardInterrupt:
            break

    consumer.close()


if __name__ == "__main__":
    main()
