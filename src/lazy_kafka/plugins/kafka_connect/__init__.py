"""Kafka Connect plugin — list and monitor connectors."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from rich.text import Text

from lazy_kafka.connect import Connect
from lazy_kafka.plugin import register
from lazy_kafka.widgets.kconnect import KConnectPanel

if TYPE_CHECKING:
    import typer
    from textual.widget import Widget

    from lazy_kafka.config import Configuration

_LOGGER = logging.getLogger(__name__)


class KafkaConnectPlugin:
    name = "kafka-connect"
    tab_label = Text.from_markup(":warning: K-connect")
    tab_id = "tab-connect"
    cli_name = None

    def build_panel(self, config: Configuration) -> Widget | str:
        try:
            hook = Connect(config.connect)
        except (ConnectionRefusedError, AssertionError) as exc:
            _LOGGER.error("kafka-connect: cannot connect", exc_info=exc)
            return "No connection"
        return KConnectPanel(id=self.tab_id, classes="has-border", hook=hook)

    def build_cli(self) -> typer.Typer | None:
        return None


register(KafkaConnectPlugin())
