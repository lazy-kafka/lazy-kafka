from __future__ import annotations

import rich.console
from textual.css.query import NoMatches
from rich.table import Table
import textual
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widget import Widget
from textual.widgets import Button, Footer, Header, Static, ListItem, ListView, Label
from rich.panel import Panel
from textual.widgets import Tree, Pretty, Rule
from textual.widgets.tree import TreeNode
from textual.color import Color
from textual.message import Message
from dataclasses import dataclass

import logging

logging.basicConfig(level=logging.INFO)
from textual import log

CONSOLE = rich.console.Console()
print(textual.__version__)

from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Static

from .kafka import *


@dataclass
class TopicData:
    topic: str
    partitions: object


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


class TopicPanel(Static):
    """A stopwatch widget."""

    def compose(self):
        j = list_topics()
        self.log("here")
        for t in j:
            yield Topic(t)

class MyScrollableContainer(ScrollableContainer):

    def on_mount(self) -> None:
        self.styles.animate("width", value=20.0, duration=1.0, easing="out_expo")
        self.log(self.tree)


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


class TopicPanelApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "style.tcss"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("escape", "unset_topic", "Toggle dark mode"),
    ]

    def on_mount(self):
        label = self.query_one("#topic")
        label.border_title = "Topics"
        label.border_subtitle = "status"
        # label = self.query_one("#details")
        # label.border_title = "Details"
        self.log(self.tree)

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        yield Header()
        yield ScrollableContainer(TopicPanel(), id="topic", classes="box")
        # yield ScrollableContainer(TopicDetails(), TopicDetailsPretty([]), id="details", classes="box")
        yield Footer()

    def on_topic_selected(self, message: Topic.Selected) -> None:
        try:
            topic_details = self.query_one(TopicDetails)
        except NoMatches as e:
            details_panel = MyScrollableContainer(TopicDetails(), id="details", classes="box initial")
            self.query_one("Screen").mount(details_panel)
            return
        topic_details.topic = (
            "[b]topic: [/b]" + str(message.topic.topic) + str(message.topic.partitions)
        )
        d = {
            "topic": message.topic.topic,
            "partitions": {
                k: {
                    "id": v.id,
                    "leader": v.leader,
                    "replicas": v.replicas,
                    "isrs": v.isrs,
                    "error": v.error,
                }
                for k, v in message.topic.partitions.items()
            },
        }
        # self.query_one(Pretty).update(d)
        self.log(f"{message.topic}")

    def action_unset_topic(self) -> None:
        """Called to remove a timer."""
        try:
            topic_details = self.query_one("#details")
        except NoMatches:
            return
        topic_details.remove()


app = TopicPanelApp()

if __name__ == "__main__":
    app = TopicPanelApp()
    app.run()
