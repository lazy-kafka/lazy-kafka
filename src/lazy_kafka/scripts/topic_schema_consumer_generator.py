from __future__ import annotations

from confluent_kafka import Consumer

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


def consume_generator(consumer, max_messages=None):
    consumer.subscribe([TOPIC])
    message_count = 0

    timeout = 1.0
    try:
        while max_messages is None or message_count < max_messages:
            try:
                # SIGINT can't be handled when polling, limit timeout to 1 second.
                msg = consumer.poll(timeout=timeout)
                if msg is None:
                    continue

                message_count += 1
                yield (
                    msg.value(),
                    SerializationContext(msg.topic(), MessageField.VALUE),
                )
            except KeyboardInterrupt:
                break
    finally:
        consumer.close()


def main():
    cfg = Configuration()

    settings = {
        "bootstrap.servers": cfg.kafka.bootstrap_servers,
        "group.id": "my-work-group-testicle",
        "auto.offset.reset": "latest",
        "security.protocol": "plaintext",
    }

    consumer = Consumer(settings)
    consumer_iterable = consume_generator(consumer)
    for _ in range(5):
        print(next(consumer_iterable))


if __name__ == "__main__":
    main()
