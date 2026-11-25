from __future__ import annotations

import logging
from collections.abc import Generator
from typing import override

from textual import work
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.css.query import NoMatches
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
from lazy_kafka.utils import get_current_time, timestamp_histogram
from lazy_kafka.widgets._status import Status
from lazy_kafka.widgets.common import WidgetWithDataTable

_LOGGER = logging.getLogger(__name__)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.widget import Widget


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
            yield Sparkline(id="message-distribution", summary_function=max)
            yield TopicDetailsWidget((self.hook), self.topic, classes="has-border")
        yield Footer(show_command_palette=False)


KafkaMessageId = str
"""Compbinastion of timestamp+key to create a unique key to message."""

SPARKLINE_BUCKETS = 100
"""Number of time buckets in the message timestamp distribution sparkline."""


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
        # The hook is injected already wired for this topic (registry config
        # and AVRO decoding included). Rebuilding it here would spawn a
        # second, uncontrolled consumer per details view.
        self.hook = hook
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
            # `raw` payload bytes are excluded: only display columns are added.
            try:
                data_table.add_row(*v.to_table_values().values(), key=k)
            except DuplicateKey:
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

        # Refresh the timestamp distribution sparkline
        self._update_sparkline(list(self.subjects.values()))

    def _update_sparkline(self, messages: list[LazyKafkaMessage]) -> None:
        """Display the timestamp distribution of the loaded messages.

        Each sparkline column is a time bucket: oldest messages on the left,
        newest on the right.
        """
        try:
            sparkline = self.screen.query_one("#message-distribution", Sparkline)
        except NoMatches:
            _LOGGER.warning("No sparkline on the screen; skipping distribution")
            return
        sparkline.data = timestamp_histogram(
            [message.timestamp for message in messages],
            num_buckets=SPARKLINE_BUCKETS,
        )

    def subject_to_table(
        self, response: list[LazyKafkaMessage], *args, **kwargs
    ) -> dict[KafkaMessageId, LazyKafkaMessage]:
        _LOGGER.debug(f"{response=}")
        return {i.offset: i for i in response}
