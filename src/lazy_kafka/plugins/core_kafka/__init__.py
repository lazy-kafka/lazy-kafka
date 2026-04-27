"""Core Kafka plugin — browse topics and tail messages."""

from __future__ import annotations

import logging
import socket
from typing import TYPE_CHECKING

from lazy_kafka.plugin import register
from lazy_kafka.topic import KafkaClient
from lazy_kafka.widgets.topic import TopicPanel

if TYPE_CHECKING:
    import typer
    from textual.widget import Widget

    from lazy_kafka.config import Configuration

_LOGGER = logging.getLogger(__name__)


class CoreKafkaPlugin:
    name = "core-kafka"
    tab_label = "Topic"
    tab_id = "tab-topic"
    cli_name = "kafka"

    def build_panel(self, config: Configuration) -> Widget | str:
        try:
            host, port_str = config.kafka.bootstrap_servers.split(":", 1)
            with socket.create_connection((host, int(port_str)), timeout=3):
                pass
            hook = KafkaClient(config.kafka)
        except OSError as exc:
            _LOGGER.error("core-kafka: cannot connect", exc_info=exc)
            return "No connection"
        return TopicPanel(id=self.tab_id, classes="has-border", hook=hook)

    def build_cli(self) -> typer.Typer | None:
        from lazy_kafka.plugins.core_kafka.cli import app

        return app


register(CoreKafkaPlugin())
