from __future__ import annotations

import logging

from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    DataTable,
    Placeholder,
    Sparkline,
)

from lazy_kafka.topic import KafkaClient
from lazy_kafka.widgets._status import Status

_LOGGER = logging.getLogger(__name__)
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from textual.app import ComposeResult


def _data():
    random.seed(73)
    return [random.expovariate(1 / 3) for _ in range(1000)]


random.seed(73)
data = [random.expovariate(1 / 3) for _ in range(1000)]


class TopicDetails(ModalScreen):
    BINDINGS = [
        ("escape", "dismiss", "X"),
    ]

    def __init__(
        self,
        topic: str,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self.hook = KafkaClient(self.app.lazy_kafka_config.kafka)
        self.topic = topic

    def compose(self) -> ComposeResult:
        yield Vertical(
            Status(),
            Sparkline(data, summary_function=max),
            DataTable(cursor_type="row"),
            Placeholder(f"This is a custom label for {self.topic}.", id="p1"),
            classes="box has-scroll",
        )

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        data = self.hook.get_last_n_messages(self.topic)
        table.add_columns(*("Offset", "Message"))
        table.add_rows(data)

