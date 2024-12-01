from __future__ import annotations

import asyncio
import logging

from textual import work
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    DataTable,
    Sparkline,
    Static,
)
from textual.worker import get_current_worker

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
        self.offset_value = (self.app.lazy_kafka_config.kafka.auto_offset_reset,)
        self.topic = topic

    def compose(self) -> ComposeResult:
        yield Vertical(
            Status(),
            Sparkline(data, summary_function=max),
            Static("Offset: ", id="initial-read-offset-label"),
            Static(f"{self.offset_value}", id="initial-read-offset"),
            DataTable(cursor_type="row"),
            classes="box has-scroll",
        )

    @work(exclusive=True)
    async def load_data_gen(self, data_table: DataTable) -> None:
        worker = get_current_worker()
        # use the aget_last_message for follow logic
        # data = await self.hook.aget_last_messages(self.topic)
        data = await self.hook.aget_last_n_messages(self.topic)
        if not worker.is_cancelled:
            for i in data:
                data_table.add_row(*i)

    async def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*("Timestamp", "Offset", "Key", "Message"))
        # for _ in range(10):
        self.load_data_gen(table)

