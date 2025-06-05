"""Apache Kafka related CLI."""
from __future__ import annotations
import logging

import rich.progress
import typer
from confluent_kafka import Consumer
from confluent_kafka.serialization import MessageField, SerializationContext
from typing_extensions import Annotated
from typing import Union
from rich import print

from lazy_kafka.config import Configuration


app = typer.Typer()

@app.callback()
def kafka():
    """Interact with [b]Apache Kafka[/]."""

def consume_generator(consumer, topic: str,  max_messages = None) :
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
                    msg.value(), SerializationContext(msg.topic(), MessageField.VALUE)
                )
            except KeyboardInterrupt:
                break
    finally:
        consumer.close()

@app.command()
def consume(topic: Annotated[str, typer.Argument(help="Name of the topic", show_default=False)]):
    """Watch for new messages in [i]`topic`[/] until stopped.

    [blue]🐣 lazy-kafka ➜ python src/lazy_kafka/scripts/topic_schema_producer.py
    """
    cfg = Configuration()
    settings = {
        "bootstrap.servers": cfg.kafka.bootstrap_servers,
        "group.id": "my-work-group",
        "auto.offset.reset": "latest",
        "security.protocol": "plaintext",
    }
    consumer = Consumer(settings)

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

