from __future__ import annotations

import logging
from typing import Self

import rich.console
import textual
from rich.text import Text
from textual import work
from textual.app import App, ComposeResult
from textual.color import Color
from textual.containers import Container, ScrollableContainer
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import reactive, Reactive
from textual.widget import Widget
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Pretty,
    Static,
    Tabs,
    Tab,
)

logging.basicConfig(level=logging.INFO)
from textual import log

CONSOLE = rich.console.Console()
print(textual.__version__)


from .kafka import TopicData, _topic_data_to_dict, list_topics
from .widgets.switcher import ContentSwitcher
from . import connect

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


class MyScrollableContainer(ScrollableContainer):
    class Completed(Message):
        """Color selected message."""

        def __init__(self) -> None:
            log(f"{self.__class__} Mounted")
            self.done = True
            super().__init__()

    def on_mount(self) -> None:
        def comp():
            self.post_message(self.Completed())

        self.styles.animate(
            "width", value=30.0, duration=1.0, easing="out_expo", on_complete=comp
        )

class TopicDetails(Widget):
    topic = reactive("")

    def render(self) -> str:
        return f"[b]TOPIC:[/b] {self.topic}"

class TopicDetailsPretty(Pretty):
    DEFAULT_CSS = """
    .hidden {
        display: none;
    }
    """

    def on_mount(self) -> None:
        self.styles.animate("opacity", value=1.0, duration=2.0)

class SchemaRegistryPanel(Container):
    pass

class KConnectPanel(Container):
    """KafkaConnect widget."""

    BORDER_SUBTITLE = "connectors"

    def __init__(self, *args, **kwargs):
        self.CONNECTORS:dict[str,str] = dict()
        self.CONNECTORS = connect.list()
        super().__init__(*args, **kwargs)
        log(self.CONNECTORS)
    pass

    def compose(self):
        yield DataTable()

    def on_mount(self):
        for data_table in self.query(DataTable):
            data_table.loading = True
            self.load_data(data_table)

    @work(exclusive=True, thread=True)
    async def load_data(self, data_table: DataTable) -> None:
        data_table.add_column("Name")
        j = self.CONNECTORS
        for t in j:
            data_table.add_row(t)
        data_table.loading = False

class PluginManager:
    # TODO: read these from plugins folder
    # or cfg
    TABS = [
        ("topic", TopicPanel, "Kafka"),
        ("schema", SchemaRegistryPanel, "Schema Registry"),
        ("connect", KConnectPanel, Text.from_markup(":warning: K-connect")),
    ]

    def get_tabs(self: Self, id: str) -> Tabs:
        _tabs = Tabs(id=id)
        for t in PluginManager.TABS:
            _tabs.add_tab(Tab(t[-1], id="tab-" + t[0]))
        return _tabs

# TODO: on tab change set the focus to the Tab widget.
# 1. this will solve the locality of bindings
# 1. will offload a lot of logic to the widgets from the main app - yay!
#    ref: https://textual.textualize.io/api/app/#textual.app.App.set_focus
# 1. maybe screens and mode_switch are better suited
#    ref: https://textual.textualize.io/guide/screens/#modes

class LazyKafka(App):
    """A Textual app to manage stopwatches."""

    topic: Reactive[TopicData] = reactive(TopicData())

    CSS_PATH = "style.tcss"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("escape", "unset_topic", "Toggle dark mode"),
        ("l", "next_tab", "Next"),
        ("h", "previous_tab", "Previous"),
        ("j", "next_widget_item", "next"),
        ("k", "previous_widget_item", "prev"),
    ]

    def on_mount(self):
        pass

    def action_next_tab(self):
        self.query_one("#tabs").action_next_tab()

    def action_previous_tab(self):
        self.query_one("#tabs").action_previous_tab()

    def action_next_widget_item(self):
        self.query_one(DataTable).action_cursor_down()

    def action_previous_widget_item(self):
        self.query_one(DataTable).action_cursor_up()

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        yield Header()

        yield Tabs(
            Tab("Kafka",id="topic"),
            Tab("Schema Registry",id="tab-schema"),
            Tab(Text.from_markup(":warning: K-connect"), id="tab-connect"),
            id="tabs",
        )
        with ContentSwitcher(initial="topic", id="vertical"):
            yield TopicPanel(id="topic", classes="box")
            yield SchemaRegistryPanel(id="tab-schema")
            yield KConnectPanel(id="tab-connect")
        yield Footer()

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """Handle TabActivated message sent by Tabs."""
        self.query_one(ContentSwitcher).current = event.tab.id  

    def on_topic_panel_selected(self, message: TopicPanel.Selected) -> None:
        """Set reactive attribute.

        Currently -> Message() -> Reactive() -> watch_topic()
        """
        self.topic = message.topic

    def watch_topic(self, topic: TopicData):
        """Callback on topic changed.

        Args:
            topic: 
        """
        try:
            topic_details = self.query_one(TopicDetails)
        except NoMatches as _:
            details_panel = MyScrollableContainer(
                TopicDetails(), Pretty([]), id="details", classes="box initial"
            )
            self.query_one(TopicPanel).mount(details_panel)
            return
        topic_details.topic = (
            "[b]topic: [/b]" + str(topic.topic) + str(topic.partitions)
        )
        self.query_one(Pretty).update(_topic_data_to_dict(topic))
        self.log(f"{topic}")

    def on_my_scrollable_container_completed(self):
        """This is quite ugly.

        I don't have anything quick to fix it up. It's not truly reactive
        as I need to wait for the animation to finish first. Then pull the values
        from the state and send attributes down.

        In that sense, it's reactive, but not 'data' reactive.

        Should be handled inside the details widget at least...
        """
        topic = self.topic
        if topic.topic is None:
            raise ValueError
        topic_details = self.query_one(TopicDetails)
        topic_details.topic = (
            "[b]topic: [/b]" + str(topic.topic) + str(topic.partitions)
        )
        self.query_one(Pretty).update(_topic_data_to_dict(topic))

    def action_unset_topic(self) -> None:
        """Called to remove a timer."""
        try:
            topic_details = self.query_one("#details")
        except NoMatches:
            return
        topic_details.remove()


app = LazyKafka()

if __name__ == "__main__":
    app = LazyKafka()
    app.run()

