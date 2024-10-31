import argparse
from uuid import uuid4

from confluent_kafka import Producer
from confluent_kafka.serialization import (
    StringSerializer,
    SerializationContext,
    MessageField,
)
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from hypothesis.strategies import text
from functools import partial
from time import sleep
from lazy_kafka.config import Configuration

def phone_number():
    return partial(text, alphabet=[chr(i) for i in range(48,58)])

class User(object):
    """
    User record

    Args:
        name (str): User's name

        favorite_number (int): User's favorite number

        favorite_color (str): User's favorite color

        address(str): User's address; confidential
    """

    def __init__(self):
        self.name = "rando name"
        self.favorite_number = 9999
        self.favorite_color = "blue"
        # address should not be serialized, see user_to_dict()
        self._address = "asdfasdf"


def user_to_dict(user, ctx):
    """
    Returns a dict representation of a User instance for serialization.

    Args:
        user (User): User instance.

        ctx (SerializationContext): Metadata pertaining to the serialization
            operation.

    Returns:
        dict: Dict populated with user attributes to be serialized.
    """

    # User._address must not be serialized; omit from dict
    return dict(
        name=user.name,
        favorite_number=user.favorite_number,
        favorite_color=user.favorite_color,
    )


def delivery_report(err, msg):
    """
    Reports the success or failure of a message delivery.

    Args:
        err (KafkaError): The error that occurred on None on success.
        msg (Message): The message that was produced or failed.
    """

    if err is not None:
        print("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    print(
        "User record {} successfully produced to {} [{}] at offset {}".format(
            msg.key(), msg.topic(), msg.partition(), msg.offset()
        )
    )


def main():
    cfg = Configuration()
    topic = "user-topic"
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
    schema_registry_conf = {"url": cfg.registry.host}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    string_serializer = StringSerializer("utf_8")
    json_serializer = JSONSerializer(schema_str, schema_registry_client, user_to_dict)

    producer = Producer({"bootstrap.servers": cfg.kafka.bootstrap_server})

    print("Producing user records to topic {}. ^C to exit.".format(topic))
    while True:
        # Serve on_delivery callbacks from previous calls to produce()
        producer.poll(0.0)
        try:
            user = User()
            producer.produce(
                topic=topic,
                key=string_serializer(str(uuid4())),
                value=json_serializer(
                    user, SerializationContext(topic, MessageField.VALUE)
                ),
                on_delivery=delivery_report,
            )
            sleep(1)
        except KeyboardInterrupt:
            break
        except ValueError:
            print("Invalid input, discarding record...")
            continue

    print("\nFlushing records...")
    producer.flush()


if __name__ == "__main__":
    main()
