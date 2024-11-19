"""Kafka topics interface. (lib confluent_kafka)"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from confluent_kafka import (
    OFFSET_BEGINNING,
    Consumer,
    TopicPartition,
)
from confluent_kafka.admin import (
    AdminClient,
    TopicMetadata,
)
from datetime import datetime, timezone

from lazy_kafka.config import KafkaConfiguration

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from confluent_kafka.admin import TopicMetadata

CONFIG = {"bootstrap.servers": "localhost:9092"}

def _timestamp_to_str(timestamp: int) -> str:
    dt = datetime.fromtimestamp(timestamp/1e3, timezone.utc)
    return dt.isoformat()


class KafkaClient:
    def __init__(self, config: KafkaConfiguration):
        self.config = config

    def list_topics(self) -> list[TopicMetadata]:
        """AdminClient"""
        admin_client = AdminClient(self.config.to_config())
        raw_topics: list[TopicMetadata] = list(
            admin_client.list_topics(timeout=1000).topics.values()
        )
        return raw_topics

    def get_last_n_messages(self, topic: str, last_n_messages: int = 10) -> list[tuple[int, str]]:
        """Retrieve last n messages from `topic`.

        Consumer instantiated.
        """
        MESSAGE_POLL_TIMEOUT_SECONDS = 1.0
        WATERMARK_TIMEOUT_SECONDS = 10.0
        READ_LAST_N_MESSAGES = 10

        consumer = Consumer(self.config.to_config())

        def get_last_n_offset(high_mark, last_n):
            if last_n > high_mark:
                # offset beginning is -2
                return OFFSET_BEGINNING
            else:
                return high_mark - last_n

        t = TopicPartition(topic, partition=0, offset=-2)
        (lo, hi) = consumer.get_watermark_offsets(
            t, timeout=WATERMARK_TIMEOUT_SECONDS, cached=False
        )

        offset = get_last_n_offset(READ_LAST_N_MESSAGES, hi)
        _LOGGER.debug("reading from offset=%s", offset)
        consumer.assign([t])
        _LOGGER.debug("%s", f"{consumer.assignment()=}")

        # compensate with 1, because we cnt-- at start
        messages = []
        i = READ_LAST_N_MESSAGES + 1
        while i := i - 1:
            try:
                # SIGINT can't be handled when polling, limit timeout to 1 second.
                msg = consumer.poll(MESSAGE_POLL_TIMEOUT_SECONDS)
                if msg is None:
                    continue
                _LOGGER.debug(
                    "%s", f"{msg.offset():<5}, {str(msg.value()):>10}, {msg.topic():>}"
                )
                # msg.timestamp(), msg.key(), msg.topic(), msg.partition(), msg.offset()
                timestamp_type = msg.timestamp()
                if timestamp_type[0] != 1:
                    # TODO: handle all types: https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#confluent_kafka.Message.timestamp
                    raise ValueError("Timestamp type not available")
                timestamp = _timestamp_to_str(timestamp_type[1])
                messages.append((timestamp, msg.offset(), msg.key(), str(msg.value())))
            # TODO: handle kafka exception
            except KeyboardInterrupt:
                break

        return messages


@dataclass
class TopicData:
    topic: Optional[str] = None
    partitions: Optional[object] = None


def topic_data_to_dict(topic: TopicData):
    d = {
        "topic": topic.topic,
        "partitions": {
            k: {
                "id": v.id,
                "leader": v.leader,
                "replicas": v.replicas,
                "isrs": v.isrs,
                "error": v.error,
            }
            for k, v in topic.partitions.items()
        },
    }
    return d


# todo create into a class with config etc. which will serve as the facade
# todo instead of returning list, turn this into generator?


if __name__ == "__main__":
    from lazy_kafka.config import Configuration

    cfg = Configuration()
    MESSAGE_POLL_TIMEOUT_SECONDS = 1.0
    WATERMARK_TIMEOUT_SECONDS = 10.0
    TOPIC = "user-topic"
    READ_LAST_N_MESSAGES = 10

    settings = {
        "bootstrap.servers": cfg.kafka.bootstrap_server,
        "group.id": "my-work-group-testicle-farts",
        "auto.offset.reset": "earliest",
        "security.protocol": "plaintext",
        "enable.auto.commit": "false",
    }

    consumer = Consumer(settings)

    def get_last_n_offset(high_mark, last_n):
        if last_n > high_mark:
            # offset beginning is -2
            return OFFSET_BEGINNING
        else:
            return high_mark - last_n

    t = TopicPartition(TOPIC, partition=0, offset=-2)
    (lo, hi) = consumer.get_watermark_offsets(
        t, timeout=WATERMARK_TIMEOUT_SECONDS, cached=False
    )

    offset = get_last_n_offset(READ_LAST_N_MESSAGES, hi)
    _LOGGER.debug("reading from offset=%s", offset)
    consumer.assign([t])
    _LOGGER.debug("%s", f"{consumer.assignment()=}")

    # compensate with 1, because we cnt-- at start
    i = READ_LAST_N_MESSAGES + 1
    while i := i - 1:
        try:
            # SIGINT can't be handled when polling, limit timeout to 1 second.
            msg = consumer.poll(MESSAGE_POLL_TIMEOUT_SECONDS)
            if msg is None:
                continue
            _LOGGER.debug(
                "%s", f"{msg.offset():<5}, {str(msg.value()):>10}, {msg.topic():>}"
            )
        except KeyboardInterrupt:
            break
