from __future__ import annotations

import logging
from typing import Any, Generator

from textual import work
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import Reactive, reactive
from textual.lazy import Lazy
from textual.widgets import (
    DataTable,
    Pretty,
)

from lazy_kafka import registry
from lazy_kafka.widgets.common import Details, MyContainer, MyScrollableContainer

logging.basicConfig(level=logging.INFO)

_LOGGER = logging.getLogger(__name__)


class SchemaRegistry(MyContainer):
    """KafkaConnect widget."""

    BORDER_TITLE = "Subjects"
    BORDER_SUBTITLE = "status"
    BINDINGS = [
        ("j", "next_widget_item", "next"),
        ("k", "previous_widget_item", "prev"),
        ("s", "load_data", "load"),
        ("escape", "unset_topic", "close"),
    ]

    details: Reactive[str] = reactive(str)

    def action_next_widget_item(self):
        self.query_one(DataTable).action_cursor_down()

    def action_previous_widget_item(self):
        self.query_one(DataTable).action_cursor_up()

    async def action_load_data(self):
        for data_table in self.query(DataTable):
            self.load_data(data_table)

    def __init__(self, *args: Any, **kwargs: Any):
        self.subjects: dict[str, str] = {"":""}
        super().__init__(*args, **kwargs)
        _LOGGER.debug(self.subjects)

    pass

    class Selected(Message):
        """Color selected message."""

        def __init__(self, details: str) -> None:
            self.details = details
            _LOGGER.debug(f"INIT: {self.details!r}")
            super().__init__()



    def compose(self) -> Any:
        yield DataTable(cursor_type="row", fixed_columns=4)
        #yield Lazy(DataTable())

    def on_mount(self):
        _LOGGER.debug("widget on mount")

    def on_schemaregistry_panel_selected(self, message: SchemaRegistry.Selected) -> None:
        """Set reactive attribute.

        Currently -> Message() -> Reactive() -> watch_topic()
        """
        _LOGGER.debug(message.details)
        self.details = message.details

    def on_data_table_focused(self, event):
        _LOGGER.debug("DATA TABLE FOC %s", f"{event!r}")


    async def on_focus(self, event):
        _LOGGER.debug("ON FOCUS!!!!!!!!!!!")
        _LOGGER.debug(event)

        for data_table in self.query(DataTable):
            self.load_data(data_table)

    def watch_details(self, details: str):
        """Callback on topic changed.

        Args:
            topic:
        """
        try:
            details_panel = self.query_one(Details)
        except NoMatches as _:
            details_panel = MyScrollableContainer(
                Details(), Pretty([]), id="details", classes="box initial"
            )
            self.mount(details_panel)
            return
        details_panel.detail_name = "[b]connector: [/b]" + str(details)
        self.query_one(Pretty).update(details)
        self.log(f"{details}")

    @work(exclusive=True)
    async def load_data(self, data_table: DataTable) -> None:
        _LOGGER.debug("here we go")
        data_table.loading = True
        sr = registry.ScheamRegistry()
        self.subjects = {i:i for i in await sr.asubjects()}
        data_table.add_column("Subjects")
        for i in self.subjects.values():
            data_table.add_row(i, key=i)
        data_table.loading = False

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        # The post_message method sends an event to be handled in the DOM
        _LOGGER.debug(f"selected: {event}")
        # log(f"selected: {self.connectors[event.value]}")
        if event.row_key.value is None:
            _LOGGER.error("False event")
            return
        self.post_message(self.Selected(self.subjects[event.row_key.value]))

    def on_my_scrollable_container_completed(self):
        """This is quite ugly.

        I don't have anything quick to fix it up. It's not truly reactive
        as I need to wait for the animation to finish first. Then pull the values
        from the state and send attributes down.

        In that sense, it's reactive, but not 'data' reactive.

        Should be handled inside the details widget at least...
        """
        details = self.details
        if details is None:
            raise ValueError
        details_panel = self.query_one(Details)
        details_panel.detail_name = "[b]connector: [/b]" + str(details)
        self.query_one(Pretty).update(details)

