from __future__ import annotations

import json
import logging

from textual import work
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import Reactive, reactive
from textual.screen import ModalScreen
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Label,
    Pretty,
    Sparkline,
    Static,
)
from textual.worker import get_current_worker

from lazy_kafka.topic import KafkaClient, LazyKafkaMessage
from lazy_kafka.utils import get_current_time
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
        ("j", "next_widget_item", "next"),
        ("k", "previous_widget_item", "prev"),
        ("f", "toggle_refresh", "Toggle follow"),
        ("escape", "dismiss", "X"),
    ]

    details: Reactive[LazyKafkaMessage | None] = reactive(None)

    def action_next_widget_item(self):
        self.query_one(DataTable).action_cursor_down()

    def action_previous_widget_item(self):
        self.query_one(DataTable).action_cursor_up()

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
        yield Header()

        with Vertical(classes="has-border has-scroll"):
            yield Status()
            yield Sparkline(data, summary_function=max)
            yield Static(f"Topic: {self.topic}", id="topic-label")
            with Horizontal(id="main-content"):
                yield DataTable(cursor_type="row")

        yield Footer(show_command_palette=False)

    def watch_details(self, details: LazyKafkaMessage):
        """Callback on topic changed.

        Args:
            topic:
        """
        try:
            details_panel = self.query_one(Pretty)
        except NoMatches as _:
            details_panel = Container(
                Pretty([]), id="details", classes="has-border initial"
            )
            _h = self.query_one("#main-content", Horizontal)
            _h.mount(details_panel)
            return
        self.query_one(Pretty).update(details)
        self.log(f"{details}")

    class Selected(Message):
        """Color selected message."""

        def __init__(self, message: LazyKafkaMessage) -> None:
            self.message = message
            super().__init__()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        # The post_message method sends an event to be handled in the DOM
        _LOGGER.debug(f"selected: {event=}")
        _LOGGER.debug(f"selected: {event!r}")
        if event.row_key.value is None:
            _LOGGER.error("False event")
            return
        self.post_message(self.Selected(self.subjects[event.row_key.value]))

    def on_topic_details_selected(self, message: TopicDetails.Selected):
        _LOGGER.debug(f"{message.message=}")
        _msg = json.loads(
            "{" + str(message.message).split(sep="{")[1].rsplit("}")[0] + "}"
        )
        self.details = _msg
        _LOGGER.debug("details updated")

    @work(exclusive=True)
    async def load_data(self, data_table: DataTable, display_load=True) -> None:
        data_table.loading = display_load
        worker = get_current_worker()
        # use the aget_last_message for follow logic
        self.subjects = {
            str(i.offset): i for i in await self.hook.aget_last_n_messages(self.topic)
        }
        if not worker.is_cancelled:
            for k, v in self.subjects.items():
                data_table.add_row(*v, key=k)

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


    def on_my_scrollable_container_completed(self):
        self.query_one(Pretty).update(self.details)
