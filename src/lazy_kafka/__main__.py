from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

import rich.console
import textual
from rich.text import Text
from textual.app import App, ComposeResult
from textual.color import Color
from textual.containers import Container, Horizontal, ScrollableContainer
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import reactive
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Pretty,
    Static,
    Tabs,
)

logging.basicConfig(level=logging.INFO)
from textual import log

CONSOLE = rich.console.Console()
print(textual.__version__)


from .kafka import TopicData, _topic_data_to_dict, list_topics


class Topic(Static):
    """A widget to display elapsed time."""

    class Selected(Message):
        """Color selected message."""

        def __init__(self, topic: TopicData) -> None:
            log(f"INIT: {topic!r}")
            self.topic = topic
            super().__init__()

    def __init__(self, topic: TopicData) -> None:
        self.topic = topic
        super().__init__()

    def on_click(self) -> None:
        # The post_message method sends an event to be handled in the DOM
        self.post_message(self.Selected(self.topic))

    def on_mount(self) -> None:
        self.styles.margin = (1, 2)
        self.styles.content_align = ("center", "middle")
        self.styles.background = Color.parse("#ffffff33")

    def render(self) -> str:
        return str(self.topic.topic)


class TopicPanel(Container):
    """A stopwatch widget."""

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
        dt = DataTable()
        dt.add_column("Name")
        j = list_topics()
        for t in j:
            dt.add_row(t.topic)
        yield dt

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


class MyTab(Tabs):
    pass


class LazyKafka(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "style.tcss"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("escape", "unset_topic", "Toggle dark mode"),
        ("l", "next_tab", "Next"),
        ("h", "previous_tab", "Previous"),
    ]
    STATE_TOPIC: Optional[TopicData] = None

    def on_mount(self):
        pass

    def action_next_tab(self):
        self.query_one("#tabs").action_next_tab()

    def action_previous_tab(self):
        self.query_one("#tabs").action_previous_tab()

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        yield Header()
        #        yield Static("One", classes="TabBar", id="tab-bar")
        yield MyTab(
            "Kafka",
            "Schema Registry",
            Text.from_markup(":warning: K-connect"),
            id="tabs",
        )
        with Horizontal(id="vertical"):
            yield TopicPanel(id="topic", classes="box")
        yield Footer()

    def on_topic_panel_selected(self, message: TopicPanel.Selected) -> None:
        log(f"{message=}")
        LazyKafka.STATE_TOPIC = message.topic
        try:
            topic_details = self.query_one(TopicDetails)
        except NoMatches as _:
            details_panel = MyScrollableContainer(
                TopicDetails(), Pretty([]), id="details", classes="box initial"
            )
            self.query_one("#vertical").mount(details_panel)
            return
        topic_details.topic = (
            "[b]topic: [/b]" + str(message.topic.topic) + str(message.topic.partitions)
        )
        self.query_one(Pretty).update(_topic_data_to_dict(message.topic))
        self.log(f"{message.topic}")

    def on_my_scrollable_container_completed(self):
        topic = LazyKafka.STATE_TOPIC
        if topic is None:
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
