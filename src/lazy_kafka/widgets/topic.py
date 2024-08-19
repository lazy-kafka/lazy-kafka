from __future__ import annotations

import logging

from textual import work
from textual.containers import Container
from textual.message import Message
from textual.widgets import (
    DataTable,
)

logging.basicConfig(level=logging.INFO)
from textual import log

from lazy_kafka.kafka import TopicData, list_topics


class TopicPanel(Container):
    """Topics widget."""

    BORDER_TITLE = "Topics"
    BORDER_SUBTITLE = "status"

    def __init__(self, *args, **kwargs):
        self.TOPICS = dict()
        for k in list_topics():
            self.TOPICS[k.topic] = k
        super().__init__(*args, **kwargs)
        log(self.TOPICS)

    class Selected(Message):
        """Color selected message."""

        def __init__(self, topic: TopicData) -> None:
            self.topic = topic
            log(f"INIT: {self.topic!r}")
            super().__init__()

    def compose(self):
        yield DataTable()

    def on_mount(self):
        for data_table in self.query(DataTable):
            data_table.loading = True
            self.load_data(data_table)

    @work(exclusive=True, thread=True)
    async def load_data(self, data_table: DataTable) -> None:
        data_table.add_column("Name")
        j = list_topics()
        for t in j:
            data_table.add_row(t.topic)
        data_table.loading = False

    def on_data_table_cell_highlighted(self, event: DataTable.CellHighlighted) -> None:
        # The post_message method sends an event to be handled in the DOM
        log(f"selected: {self.TOPICS[event.value]}")
        self.post_message(self.Selected(self.TOPICS[event.value]))
