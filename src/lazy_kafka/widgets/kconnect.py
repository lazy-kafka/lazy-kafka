from __future__ import annotations

import logging
from typing import Any, Generator

from textual import work
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import Reactive, reactive
from textual.widgets import (
    DataTable,
    Pretty,
)

from lazy_kafka import connect
from lazy_kafka.widgets.common import Details, MyContainer, MyScrollableContainer

logging.basicConfig(level=logging.INFO)

_LOGGER = logging.getLogger(__name__)


class KConnectPanel(MyContainer):
    """KafkaConnect widget."""

    BORDER_TITLE = "Connectors"
    BORDER_SUBTITLE = "status"
    BINDINGS = [
        ("j", "next_widget_item", "next"),
        ("k", "previous_widget_item", "prev"),
        ("escape", "unset_topic", "close"),
    ]

    details: Reactive[connect.ConnectorData] = reactive(connect.ConnectorData())

    def action_next_widget_item(self):
        self.query_one(DataTable).action_cursor_down()

    def action_previous_widget_item(self):
        self.query_one(DataTable).action_cursor_up()

    def __init__(self, *args: Any, **kwargs: Any):
        self.connectors: dict[str, connect.ConnectorData] = dict()
        self.connectors = connect.list()
        super().__init__(*args, **kwargs)
        _LOGGER.debug(self.connectors)

    pass

    class Selected(Message):
        """Color selected message."""

        def __init__(self, details: connect.ConnectorData) -> None:
            self.details = details
            _LOGGER.debug(f"INIT: {self.details!r}")
            super().__init__()

    def compose(self) -> Generator[DataTable[Any], Any, None]:
        yield DataTable()

    def on_mount(self):
        for data_table in self.query(DataTable):
            data_table.loading = True
            data_table.cursor_type = "row"
            data_table.fixed_columns = 4
            self.load_data(data_table)

    def on_kconnect_panel_selected(self, message: KConnectPanel.Selected) -> None:
        """Set reactive attribute.

        Currently -> Message() -> Reactive() -> watch_topic()
        """
        _LOGGER.debug(message.details)
        self.details = message.details

    def watch_details(self, details: connect.ConnectorData):
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
        details_panel.detail_name = "[b]connector: [/b]" + str(details.name)
        self.query_one(Pretty).update(details.to_dict())
        self.log(f"{details}")

    @work(exclusive=True, thread=True)
    async def load_data(self, data_table: DataTable) -> None:
        data_table.add_column("Name")
        data_table.add_column("State")
        data_table.add_column("Worker ID")
        data_table.add_column("Type")
        for i in map(lambda x: x.to_tuple(), self.connectors.values()):
            data_table.add_row(*i, key=i[0])
        # data_table.add_rows(map(lambda x: x.to_tuple(), self.connectors.values()))
        data_table.loading = False

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        # The post_message method sends an event to be handled in the DOM
        _LOGGER.debug(f"selected: {event}")
        # log(f"selected: {self.connectors[event.value]}")
        if event.row_key.value is None:
            _LOGGER.error("False event")
            return
        self.post_message(self.Selected(self.connectors[event.row_key.value]))

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
        details_panel.detail_name = "[b]connector: [/b]" + str(details.name)
        self.query_one(Pretty).update(details.to_dict())

