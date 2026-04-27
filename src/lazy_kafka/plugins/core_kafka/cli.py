"""Apache Kafka related CLI."""

from __future__ import annotations

import json
import logging
import random
from pathlib import Path
from time import sleep
from typing import Annotated, Any
from uuid import uuid4

import rich.progress
import typer
from confluent_kafka import Consumer, Producer
from confluent_kafka.serialization import (
    MessageField,
    SerializationContext,
    StringSerializer,
)
from rich import print

from lazy_kafka.config import Configuration

_LOGGER = logging.getLogger(__name__)

CONSOLE = rich.console.Console(log_path=False)

app = typer.Typer()


@app.callback()
def kafka():
    """Interact with [b]Apache Kafka[/]."""


def consume_generator(consumer, topic: str, max_messages=None):
    consumer.subscribe([topic])
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


# NOTE: the commands below repeat the config file path option, this is due
# to ctx object not playing nice and me not grasping fully:
# https://github.com/fastapi/typer/discussions/1195
@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def consume(
    ctx: typer.Context,
    topic: Annotated[str, typer.Argument(help="Name of the topic", show_default=False)],
    config_file: Annotated[
        Path,
        typer.Option(
            "--config-file",
            "-f",
            help="Path to lazy-kafka config file.",
            rich_help_panel="[i][green]Customization and Utils[/]",
        ),
    ] = Configuration.default_config_file_path(),
):
    """Watch for new messages in [i]`topic`[/] until stopped.

    [blue]🐣 lazy-kafka ➜ python src/lazy_kafka/scripts/topic_schema_producer.py
    """
    cfg = Configuration().from_toml(config_file)
    consumer = Consumer(cfg.kafka.to_config())

    consumer_iterable = consume_generator(consumer, topic)
    with rich.progress.Progress(
        rich.progress.SpinnerColumn(),
        rich.progress.TextColumn("[progress.description]{task.description}"),
        rich.progress.BarColumn(),
        rich.progress.TimeElapsedColumn(),
        transient=True,
    ) as prog:
        prog.add_task("[green]Consuming")
        while True:
            try:
                msg = next(consumer_iterable)
                if msg:
                    prog.log(msg[0])
            except StopIteration:
                # continue polling even if no more new msg
                continue


@app.command()
def produce(
    topic: Annotated[str, typer.Argument(help="Name of the topic", show_default=False)],
    config_file: Annotated[
        Path,
        typer.Option(
            "--config-file",
            "-f",
            help="Path to lazy-kafka config file.",
            rich_help_panel="[i][green]Customization and Utils[/]",
        ),
    ] = Configuration.default_config_file_path(),
):
    """Produce new messages in [i]`topic`[/] until stopped.

    The producer functionality is only for testing purposes.

    Produce messages in different ways:
      - no schema, raw payload
      - JSONSchema
      - AVRO Schema
      - Protobuff
    """
    print("Press <C>+C to stop producing messages.")
    _produce(topic, config_file)


def _produce(topic: str, config_file: Path):
    def _data_to_dict(_d: dict, ctx: Any) -> dict:
        return _d

    cfg = Configuration().from_toml(config_file)
    producer = Producer(cfg.kafka.to_config())
    string_serializer = StringSerializer("utf_8")

    print(f"Producing user records to topic {topic}. ^C to exit.")

    def _user():
        return json.dumps(
            {
                "confidence": random.random(),
                "createdDateTimeUTC": "2025-06-18T13:08:20.423076",
                "isRain": True,
                "validUntil": "2025-06-18T13:09:20.423076",
                "snow": {"shape": "good"},
            }
        )

        return dict(
            name=str([chr(random.randint(97, 122)) for _ in range(4)]),
            favorite_number=random.randint(0, 10),
            favorite_color=random.choice(["blue", "red"]),
        )

    with rich.progress.Progress(
        rich.progress.SpinnerColumn(),
        rich.progress.TextColumn("[progress.description]{task.description}"),
        rich.progress.BarColumn(style="blue", pulse_style="#3879ba"),
        rich.progress.TimeElapsedColumn(),
        transient=False,
        console=CONSOLE,
    ) as prog:
        prog.add_task("[bold]Producing", total=None)

        def _delivery_report(err, msg):
            """
            Reports the success or failure of a message delivery.

            Args:
                err (KafkaError): The error that occurred on None on success.
                msg (Message): The message that was produced or failed.
            """
            if err is not None:
                _LOGGER.info(f"Delivery failed for User record {msg.key()}: {err}")
                return
            prog.log(
                f"Record {msg.key()} successfully produced to [blue]{msg.topic()}[/] partition-{msg.partition()} at offset [orange]{msg.offset()}[/]."
            )

        while True:
            # Serve on_delivery callbacks from previous calls to produce()
            producer.poll(0.0)
            try:
                producer.produce(
                    topic=topic,
                    key=string_serializer(str(uuid4())),
                    value=_user(),
                    on_delivery=_delivery_report,
                )
                sleep(1)
            except KeyboardInterrupt:
                break
            except ValueError:
                print("Invalid input, discarding record...")
                continue

    print("\n🌪️🚽Flushing final records...")
    producer.flush()
