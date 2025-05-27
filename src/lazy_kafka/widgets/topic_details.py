from __future__ import annotations

import logging
from typing import Generator, override

from textual import work
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.reactive import Reactive, reactive
from textual.screen import ModalScreen
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Label,
    Sparkline,
)
from textual.widgets.data_table import DuplicateKey, RowDoesNotExist

from lazy_kafka.topic import KafkaTopicDetailsClient, LazyKafkaMessage
from lazy_kafka.utils import get_current_time
from lazy_kafka.widgets._status import Status
from lazy_kafka.widgets.common import WidgetWithDataTable

_LOGGER = logging.getLogger(__name__)
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.widget import Widget


random.seed(73)
data = [random.expovariate(1 / 3) for _ in range(1000)]


class TopicDetails(ModalScreen):
    def __init__(
        self,
        topic: str,
        hook: KafkaTopicDetailsClient,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        # self.hook = KafkaClient(self.app.lazy_kafka_config.kafka)
        # self.offset_value = (self.app.lazy_kafka_config.kafka.auto_offset_reset,)
        self.topic = topic
        self.hook = hook
        # self.data_auto_refresh = False

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="has-scroll"):
            yield Sparkline(data, summary_function=max)
            yield TopicDetailsWidget((self.hook), self.topic, classes="has-border")
        yield Footer(show_command_palette=False)


KafkaMessageId = str
"""Compbinastion of timestamp+key to create a unique key to message."""


class TopicDetailsWidget(WidgetWithDataTable[KafkaMessageId, list[LazyKafkaMessage]]):
    """Topics widget."""

    BORDER_TITLE = "Topics"
    BORDER_SUBTITLE = "status"

    BINDINGS = [
        ("escape", "app.pop_screen", "close"),
    ]

    selected_id: Reactive[str] = reactive(str)
    details: Reactive[LazyKafkaMessage | None] = reactive(None)

    def __init__(self, hook: KafkaTopicDetailsClient, topic: str, *args, **kwargs):
        self.subjects = dict()
        self.hook = KafkaTopicDetailsClient(hook.config)
        self.topic = topic

        self.data_auto_refresh = False
        super().__init__(*args, **kwargs)
        _LOGGER.debug(self.subjects)

    def compose(self) -> Generator[Widget]:
        yield Status()
        yield DataTable(cursor_type="row", zebra_stripes=True)

    def on_mount(self):
        self.border_title = f"[i]Topic:[/] {self.topic}"
        data_table = self.query_one(DataTable)
        data_table.add_columns(*("Timestamp", "Offset", "Key", "Message"))
        super().on_mount()

    @override
    @work(exclusive=True)
    async def load_data(self, data_table: DataTable, display_load=True) -> None:
        """Load data.

        Args:
            display_load (bool): set to false to disable loading animation.
            data_table: DataTable instance to be updated.
        """
        data_table.loading = display_load
        _response = await self.hook.asubjects(self.topic)
        self.subjects = self.subject_to_table(_response)
        _LOGGER.debug(f"self.subjects is None: {self.subjects is None}")
        for k, v in self.subjects.items():
            try:
                data_table.add_row(*v, key=k)
            except DuplicateKey:
                # No details are shown in rows, so it's ok to just pass
                continue
        # Set the cursor to the same row
        # TODO: emit data-loaded event and react to that with "move_cursor"
        try:
            _new_index_of_old_row = data_table.get_row_index(self.selected_id)
        except RowDoesNotExist:
            _new_index_of_old_row = None
        if _new_index_of_old_row:
            data_table.move_cursor(row=_new_index_of_old_row)

        data_table.loading = False
        label = self.query_one("#time", Label)
        label.update(f"{get_current_time()}")

    def subject_to_table(
        self, response: list[LazyKafkaMessage], *args, **kwargs
    ) -> dict[KafkaMessageId, LazyKafkaMessage]:
        _LOGGER.debug(f"LOFASZ: {response}")
        return {i.offset: i for i in response}
