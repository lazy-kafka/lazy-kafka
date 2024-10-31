from __future__ import annotations

import logging

from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    DataTable,
    Placeholder,
    Sparkline,
)

from lazy_kafka.widgets._status import Status
from lazy_kafka.widgets.common import MyScrollableContainer
from lazy_kafka.topic import get_last_n_messages

_LOGGER = logging.getLogger(__name__)
import random

def _data():
    random.seed(73)
    return [random.expovariate(1 / 3) for _ in range(1000)]

random.seed(73)
data = [random.expovariate(1 / 3) for _ in range(1000)]




ROWS = [
    ("Offset", "Key", "Message", "DateTime"),
    (4, "Joseph Schooling", "Singapore", "2024-01-23 13:23:33.555"),
    (2, "Michael Phelps", "United States", "2024-01-23 13:23:33.555"),
    (5, "Chad le Clos", "South Africa", "2024-01-23 13:23:33.555"),
    (6, "László Cseh", "Hungary", "2024-01-23 13:23:33.555"),
    (3, "Li Zhuhao", "China", "2024-01-23 13:23:33.555"),
    (8, "Mehdy Metella", "France", "2024-01-23 13:23:33.555"),
    (7, "Tom Shields", "United States", "2024-01-23 13:23:33.555"),
    (1, "Aleksandr Sadovnikov", "Russia", "2024-01-23 13:23:33.555"),
    (10, "Darren Burns", "Scotland", "2024-01-23 13:23:33.555"),
    (4, "Joseph Schooling", "Singapore", "2024-01-23 13:23:33.555"),
    (2, "Michael Phelps", "United States", "2024-01-23 13:23:33.555"),
    (5, "Chad le Clos", "South Africa", "2024-01-23 13:23:33.555"),
    (6, "László Cseh", "Hungary", "2024-01-23 13:23:33.555"),
    (3, "Li Zhuhao", "China", "2024-01-23 13:23:33.555"),
    (8, "Mehdy Metella", "France", "2024-01-23 13:23:33.555"),
    (7, "Tom Shields", "United States", "2024-01-23 13:23:33.555"),
    (1, "Aleksandr Sadovnikov", "Russia", "2024-01-23 13:23:33.555"),
    (10, "Darren Burns", "Scotland", "2024-01-23 13:23:33.555"),
    (4, "Joseph Schooling", "Singapore", "2024-01-23 13:23:33.555"),
    (2, "Michael Phelps", "United States", "2024-01-23 13:23:33.555"),
    (5, "Chad le Clos", "South Africa", "2024-01-23 13:23:33.555"),
    (6, "László Cseh", "Hungary", "2024-01-23 13:23:33.555"),
    (3, "Li Zhuhao", "China", "2024-01-23 13:23:33.555"),
    (8, "Mehdy Metella", "France", "2024-01-23 13:23:33.555"),
    (7, "Tom Shields", "United States", "2024-01-23 13:23:33.555"),
    (1, "Aleksandr Sadovnikov", "Russia", "2024-01-23 13:23:33.555"),
    (10, "Darren Burns", "Scotland", "2024-01-23 13:23:33.555"),
]

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
        data = get_last_n_messages(self.topic)
        table.add_columns(*("Offset", "Message"))
        table.add_rows(data)
