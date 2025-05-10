from __future__ import annotations

import logging
import time
from typing import Any

from textual import work
from textual.containers import Vertical
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import Reactive, reactive
from textual.widgets import (
    DataTable,
    Label,
    Pretty,
)
from textual.widgets.data_table import DuplicateKey

from lazy_kafka import connect
from lazy_kafka.widgets._status import Status
from lazy_kafka.widgets.common import Details, MyContainer, MyScrollableContainer
from lazy_kafka.widgets.topic_details import TopicDetails

from lazy_kafka.utils import get_current_time

logging.basicConfig(level=logging.INFO)

_LOGGER = logging.getLogger(__name__)


def _apply_styling(d: connect.ConnectorData) -> connect.ConnectorData:
    """

    Possible states:
        RUNNING
        FAILED
        RESTARTING

    Args:
        d:

    Returns:

    """
    if d.state == "RUNNING":
        state = f"[italic green]{d.state}[/italic green]"
    elif d.state == "FAILED":
        state = f"[italic red]{d.state}[/italic red]"
    else:
        state = d.state

    _d2 = connect.ConnectorData(
        d.name,
        state,
        d.worker_id,
        d.type,
    )
    return _d2


def connector_to_data_table_row(data: connect.ConnectorData) -> tuple:
    return _apply_styling(data).to_tuple()


class KConnectPanel(MyContainer):
    """KafkaConnect widget."""

    BORDER_TITLE = "Connectors"
    BORDER_SUBTITLE = "status"
    BINDINGS = [
        ("j", "next_widget_item", "↓"),
        ("k", "previous_widget_item","↑"),
        ("f", "toggle_refresh", "Toggle follow"),
        ("escape", "unset_topic", "Close"),
    ]

    details: Reactive[connect.ConnectorData] = reactive(connect.ConnectorData())

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

    def __init__(self, *args: Any, **kwargs: Any):
        self.connectors: dict[str, connect.ConnectorData] = {}
        # NOTE: maybe fetching config from App is not the best design
        self.hook = connect.Connect(self.app.lazy_kafka_config.connect.host)
        self.data_auto_refresh = False
        super().__init__(*args, **kwargs)
        _LOGGER.debug(self.connectors)

    class Selected(Message):
        """Color selected message."""

        def __init__(self, details: connect.ConnectorData) -> None:
            self.details = details
            _LOGGER.debug(f"INIT: {self.details!r}")
            super().__init__()

    def compose(self) -> Any:
        yield Vertical(
            Status(),
            DataTable(cursor_type="row", zebra_stripes=True),
        )

    def on_mount(self):
        """Initialize data table with columns"""
        data_table = self.query_one(DataTable)
        data_table.add_column("Name")
        data_table.add_column("State")
        data_table.add_column("Worker ID")
        data_table.add_column("Type")
        self.update_timer = self.set_interval(2, self.action_load_data, pause=True)

    def on_kconnect_panel_selected(self, message: KConnectPanel.Selected) -> None:
        """Set reactive attribute.

        Currently -> Message() -> Reactive() -> watch_topic()
        """
        _LOGGER.debug("%s", message.details)
        self.details = message.details

    async def on_focus(self, event):
        """Perform a single refresh on focus."""
        for data_table in self.query(DataTable):
            self.load_data(data_table)

    def watch_details(self, details: connect.ConnectorData):
        """Callback on topic changed.

        Args:
            topic:
        """
        try:
            details_panel = self.query_one(Details)
        except NoMatches as _:
            details_panel = MyScrollableContainer(
                Details(), Pretty([]), id="details", classes="has-border initial"
            )
            self.mount(details_panel)
            return
        details_panel.detail_name = "[b]connector: [/b]" + str(details.name)
        self.query_one(Pretty).update(details.to_dict())
        self.log(f"{details}")

    @work(exclusive=True)
    async def load_data(self, data_table: DataTable, display_load=True) -> None:
        data_table.loading = display_load
        _resp = await self.hook.alist()
        self.connectors = connect.ConnectorData.from_response(_resp)
        for connector in self.connectors.values():
            try:
                data_table.add_row(
                    *connector_to_data_table_row(connector), key=connector.name
                )
            except DuplicateKey:
                # This is useful, if I do not maintain the internal state of
                # currently selected "subject". I use the other approach on the
                # registry screen.
                _current_row_index = data_table.cursor_row
                _current_row_key = data_table.get_row_at(_current_row_index)[0]
                data_table.remove_row(row_key=connector.name)
                data_table.add_row(
                    *connector_to_data_table_row(connector), key=connector.name
                )
                try:
                    #TODO: move one up if the row was removed
                    _new_index_of_old_row = data_table.get_row_index(_current_row_key)
                except ValueError:
                    pass
                data_table.move_cursor(row=_new_index_of_old_row)


        data_table.loading = False
        label = self.query_one("#time", Label)
        label.update(f"{get_current_time()}")

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
