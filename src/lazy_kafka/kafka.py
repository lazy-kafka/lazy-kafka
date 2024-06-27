"""Kafka interface"""

from typing import TYPE_CHECKING
from confluent_kafka.admin import AdminClient

if TYPE_CHECKING:
    from confluent_kafka.admin import TopicMetadata

CONFIG = {"bootstrap.servers": "localhost:9092"}


def list_topics():
    admin_client = AdminClient(CONFIG)
    raw_topics: List[TopicMetadata] = list(
        admin_client.list_topics(timeout=1000).topics.values()
    )

    return raw_topics
