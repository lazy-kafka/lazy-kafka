from __future__ import annotations

import logging

from textual import work
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    DataTable,
    Sparkline,
    Static,
    Label
)
from textual.worker import get_current_worker

from lazy_kafka.topic import KafkaClient
from lazy_kafka.widgets._status import Status

from lazy_kafka.utils import get_current_time

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
        ("f", "toggle_refresh", "Toggle follow"),
        ("escape", "dismiss", "X"),
    ]

    def action_stop_refresh(self):
        self.update_timer.pause()
        label = self.query_one("#icon", Label)
        label.remove_class("-live")
        self.data_auto_refresh = False

    def action_start_refresh(self):
        self.update_timer.resume()
        label = self.query_one("#icon", Label)
        label.add_class("-live")
        self.data_auto_refresh = True

    def action_toggle_refresh(self):
        if self.data_auto_refresh:
            self.action_stop_refresh()
        else:
            self.action_start_refresh()

    async def action_load_data(self):
        for data_table in self.query(DataTable):
            self.load_data(data_table, display_load=False)

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
        self.data_auto_refresh = False

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
    async def load_data(self, data_table: DataTable, display_load=True) -> None:
        data_table.loading = display_load
        worker = get_current_worker()
        # use the aget_last_message for follow logic
        data = await self.hook.aget_last_n_messages(self.topic)
        if not worker.is_cancelled:
            for i in data:
                data_table.add_row(*i)

        data_table.loading = False
        label = self.query_one("#time", Label)
        label.update(f"{get_current_time()}")
        # todo: update the bar graph with a single line: height len(messages)

    async def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*("Timestamp", "Offset", "Key", "Message"))
        # for _ in range(10):
        self.load_data(table)
        self.update_timer = self.set_interval(2, self.action_load_data, pause=True)

