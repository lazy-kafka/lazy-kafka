from __future__ import annotations

import logging
from typing import Any, Generator, TypeAlias

from textual import work
from textual.containers import Container
from textual.message import Message
from textual.widgets import (
    DataTable,
)

logging.basicConfig(level=logging.INFO)
from textual import log

from lazy_kafka import connect


class KConnectPanel(Container):
    """KafkaConnect widget."""

    BORDER_SUBTITLE = "connectors"

    def __init__(self, *args: Any, **kwargs: Any):
        self.connectors: dict[str, connect.ConnectorData] = dict()
        self.connectors = {i.name: i for i in connect.list()}
        super().__init__(*args, **kwargs)
        log(self.connectors)

    pass


    class Selected(Message):
        """Color selected message."""

        def __init__(self, details: connect.ConnectorData) -> None:
            self.details = details
            log(f"INIT: {self.details!r}")
            super().__init__()


    def compose(self) -> Generator[DataTable[Any], Any, None]:
        yield DataTable()

    def on_mount(self):
        for data_table in self.query(DataTable):
            data_table.loading = True
            self.load_data(data_table)

    @work(exclusive=True, thread=True)
    async def load_data(self, data_table: DataTable) -> None:
        data_table.add_column("Name")
        j = self.connectors
        for t in j:
            data_table.add_row(t)
        data_table.loading = False

    def on_data_table_cell_highlighted(self, event: DataTable.CellHighlighted) -> None:
        # The post_message method sends an event to be handled in the DOM
        log(f"selected: {self.connectors[event.value]}")
        self.post_message(self.Selected(self.connectors[event.value]))
