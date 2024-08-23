"""Kafka topics interface. (lib confluent_kafka)"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from confluent_kafka.admin import AdminClient

if TYPE_CHECKING:
    from confluent_kafka.admin import TopicMetadata

CONFIG = {"bootstrap.servers": "localhost:9092"}


def list_topics() -> list[TopicMetadata]:
    admin_client = AdminClient(CONFIG)
    raw_topics: list[TopicMetadata] = list(
        admin_client.list_topics(timeout=1000).topics.values()
    )

    return raw_topics


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
