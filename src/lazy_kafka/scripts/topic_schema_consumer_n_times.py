from __future__ import annotations

from confluent_kafka import (
    KafkaError,
    TopicPartition,
)

from lazy_kafka.config import Configuration, KafkaConfiguration
from lazy_kafka.topic import KafkaClient, NoMessagesError, OffsetInvalidError


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


def consume_generator(consumer: KafkaClient, topic: str, n: int = 10):
    from rich.pretty import pprint

    partitions = consumer.get_topic_partitions(topic)
    # ----
    partition_offsets = consumer.get_partition_offsets(partitions, n)
    partition_assignments = []
    for partition, (start_offset, high_offset) in partition_offsets.items():
        if start_offset == 0 and high_offset == 0:
            # Do not append it to topic list
            continue
        # This is a naive strategy, reading n messages from each partition
        print(f"{start_offset=} {high_offset=}")
        tp = TopicPartition(partition.topic, partition.partition, start_offset)
        partition_assignments.append(tp)

    pprint(partition_assignments)

    consumer.assign(partition_assignments)

    # Collect messages
    messages = []
    message_count = 0
    max_messages_total = n

    # Set a reasonable timeout for the whole operation
    while message_count < max_messages_total:
        # Check timeout
        # Poll for message
        try:
            msg = consumer.poll()
        except OffsetInvalidError:
            consumer.step_offset()
        except NoMessagesError:
            # No message within timeout - check if we've reached the end of all partitions
            # TODO: move this into a member function -> all_done vs not
            #       can be challenging, should partition state be attached to the KafkaClient???
            all_done = True
            for partition in partition_assignments:
                current_position = consumer.position([partition])[0]
                _, high_offset = partition_offsets[
                    TopicPartition(partition.topic, partition.partition, 0)
                ]
                current_offset = current_position.offset
                if current_offset < high_offset:
                    all_done = False
                    break

            # NOTE: break out of the loop here
            if all_done:
                break
            continue

        if msg.error():
            print("---Message---")
            print(f"{msg.value()}")
            print(f"{msg.error().reason()}")
            print("")
            error_code = msg.error().code()
            if error_code == KafkaError._PARTITION_EOF:
                # End of partition, not an error
                continue
            else:
                print(f"Consumer error: {msg.error()}")
                continue

        # Process message
        value = {"msg": msg.value()}
        value["_kafka_metadata"] = {
            "topic": msg.topic(),
            "partition": msg.partition(),
            "offset": msg.offset(),
            "timestamp": msg.timestamp()[1] if msg.timestamp() else None,
        }
        messages.append(value)
        message_count += 1

    # Sort messages by timestamp if available
    messages.sort(key=lambda m: m.get("_kafka_metadata", {}).get("timestamp", 0))

    # Return the latest N messages
    return messages[-n:] if len(messages) > n else messages


def main(topic: str):
    cfg = Configuration()

    settings = KafkaConfiguration(
        **{
            "bootstrap_servers": cfg.kafka.bootstrap_servers,
            "group_id": "my-work-group-testicle",
            "auto_offset_reset": "latest",
            "security_protocol": "plaintext",
        }
    )

    consumer = KafkaClient(settings)
    messages = consume_generator(consumer, topic)

    return messages


if __name__ == "__main__":
    import typer
    from rich.console import Console
    from rich.pretty import pprint
    from rich.table import Table

    app = typer.Typer()

    @app.command()
    def _main(topic: str):
        messages = main(topic)
        console = Console()
        table = Table("Name", "Item")
        pprint(messages)
        for m in messages:
            table.add_row(str(m["_kafka_metadata"]["offset"]), str(m["msg"]))
        console.print(table)

    app()
