from __future__ import annotations

import rich.console
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


class TopicDetails(Widget):
    topic = reactive("")

    def render(self) -> str:
        return f"[b]TOPIC:[/b] {self.topic}"

class TopicPanelApp(App):
    """A Textual app to manage stopwatches."""

    #CSS_PATH = "style.tcss"

    def on_mount(self):
        label = self.query_one("#topic")
        label.border_title = "Topics"
        label.border_subtitle = "status"
        #self.panel.styles.color = Color(191, 78, 96)
        self.log(self.tree)

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        yield Header()
        yield TopicPanel(id="topic")
        #yield TopicDetails(classes="box")
        yield Rule(line_style="thick")
        yield Rule(line_style="dashed")
        yield TopicDetails()
        yield Footer()

    def on_topic_selected(self, message: Topic.Selected) -> None:
        self.log(message.topic)
        self.query_one(TopicDetails).topic = "topic: "+str(message.topic.topic)+str(message.topic.partitions)
        self.log(f"------------------{message.topic}")

app = TopicPanelApp()

if __name__ == "__main__":
    app = TopicPanelApp()
    app.run()
