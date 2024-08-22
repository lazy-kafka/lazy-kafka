from __future__ import annotations

import logging
from typing import Any, Generator

from textual.css.query import NoMatches
from textual.reactive import Reactive, reactive
from textual import work
from textual.containers import Container
from textual.message import Message
from textual.widgets import (
    DataTable,
)

from textual.widget import Widget

from lazy_kafka.widgets.common import MyContainer
logging.basicConfig(level=logging.INFO)
from textual import log

_LOGGER = logging.getLogger(__name__)
from lazy_kafka import connect


from textual import work
from textual.containers import ScrollableContainer
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import Reactive, reactive
from textual.widget import Widget
from textual.widgets import (
    DataTable,
    Pretty,
)

class MyScrollableContainer(ScrollableContainer):
    class Completed(Message):
        """Color selected message."""

        def __init__(self) -> None:
            _LOGGER.debug("%s Mounted", self.__class__)
            self.done = True
            super().__init__()

    def on_mount(self) -> None:
        def comp():
            self.post_message(self.Completed())

        self.styles.animate(
            "width", value=30.0, duration=1.0, easing="out_expo", on_complete=comp
        )


class Details(Widget):
    topic = reactive("")

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = "topic-details",
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )

#################




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
        _LOGGER.debug("KCONNECT NEXT")
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
            data_table.cursor_type="row"
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
        details_panel.topic = (
            "[b]connector: [/b]" + str(details.name)
        )
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
        #data_table.add_rows(map(lambda x: x.to_tuple(), self.connectors.values()))
        data_table.loading = False

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        _LOGGER.debug("SNOHEUNSTHEOU")
        # The post_message method sends an event to be handled in the DOM
        _LOGGER.debug(f"selected: {event}")
        #log(f"selected: {self.connectors[event.value]}")
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
        details_panel.topic = (
            "[b]connector: [/b]" + str(details.name)
        )
        self.query_one(Pretty).update(details.to_dict())


    def action_unset_topic(self) -> None:
        """Called to remove a timer."""
        try:
            topic_details = self.query_one("#details")
        except NoMatches:
            return
        topic_details.remove()
