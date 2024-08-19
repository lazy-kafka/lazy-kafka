from __future__ import annotations

import logging
from typing import Self

import rich.console
import textual
from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import Reactive, reactive
from textual.widget import Widget
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Pretty,
    Tab,
    Tabs,
)

logging.basicConfig(level=logging.INFO)
from textual import log

CONSOLE = rich.console.Console()
print(textual.__version__)


from .kafka import TopicData, topic_data_to_dict
from .connect import ConnectorData
from .widgets.kconnect import KConnectPanel
from .widgets.switcher import ContentSwitcher
from .widgets.topic import TopicPanel

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

class ConnectorDetails(Widget):
    connector = reactive("")

    def render(self) -> str:
        return f"[b]CONNECTOR:[/b] {self.connector}"

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
    connector: Reactive[ConnectorData] = reactive(ConnectorData())


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
        self.query_one(Pretty).update(topic_data_to_dict(topic))
        self.log(f"{topic}")


    def watch_connect(self, topic: ConnectorData):
        """Callback on topic changed.

        Args:
            topic: 
        """
        try:
            topic_details = self.query_one(ConnectorDetails)
        except NoMatches as _:
            details_panel = MyScrollableContainer(
                TopicDetails(), Pretty([]), id="details", classes="box initial"
            )
            self.query_one(KConnectPanel).mount(details_panel)
            return
        topic_details.connector = (
            "[b]connector: [/b]" + str(topic.name) + str(topic.status)
        )
        self.query_one(Pretty).update(topic)
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
        self.query_one(Pretty).update(topic_data_to_dict(topic))

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

