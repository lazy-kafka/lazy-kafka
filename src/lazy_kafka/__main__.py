from __future__ import annotations

import rich.console
from rich.table import Table
import textual
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widget import Widget
from textual.widgets import Button, Footer, Header, Static, ListItem, ListView, Label
from rich.panel import Panel
from textual.widgets import Tree, Pretty
from textual.widgets.tree import TreeNode
from textual.color import Color
from textual.message import Message

import logging

CONSOLE = rich.console.Console()
print(textual.__version__)


from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Static

from .kafka import *

class TopicDetails(Widget):

    topic_details = reactive({"no":"det"})

    def compose(self):
        yield Pretty(self.topic_details)

    def watch_topic_details(self, topic_details):
        try:
            self.query_one(Pretty).update(topic_details)
        except:
            pass

class TopicList(Widget):
    """A widget to display elapsed time."""
    BINDINGS = [
        ("a", "add_stopwatch", "Add"),
        ("h", "vleft", "Move left"),
        ("j", "vdown", "Motion down"),
        ("k", "vup", "up"),
        ("l", "vright", "right"),
        ("x", "details", "get details"),
    ]
    
    class Selected(Message):
        
        def __init__(self, topic: str) -> None:
            self.topic = topic
            super().__init__()

    def action_details(self) -> None:
        """Show details in TopicDetails widget."""
        self.query_one(TopicDetails).details = {"hello": {"world": "!"}}

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark
    
    def action_vright(self) -> None:
        """Add a node to the tree."""
        tree = self.query_one(Tree)
        tree.root.expand()

    def action_vleft(self) -> None:
        """Add a node to the tree."""
        tree = self.query_one(Tree)
        tree.root.collapse()

    def action_vdown(self) -> None:
        """Add a node to the tree."""
        tree = self.query_one(Tree)
        tree.action_cursor_down()

    def action_vup(self) -> None:
        """Add a node to the tree."""
        tree = self.query_one(Tree)
        tree.action_cursor_up()
        tree.show_guides=False

    def on_click(self):
        self.post_message(self.Selected(self.topic))

    def compose(self):
        tree = Tree("root", id="topicTree")
        tree.root.expand()
        j = list_topics()
        for t in j:
            tree.root.add_leaf(t.topic)
        yield tree

class TopicPanel(Static):
    """A stopwatch widget."""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "start":
            self.add_class("started")
        elif event.button.id == "stop":
            self.remove_class("started")

    def compose(self) -> ComposeResult:
        """Create child widgets of a stopwatch."""
        yield ScrollableContainer(TopicList())

class TopicPanelApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "style.tcss"
    topic_details = reactive({})

    def on_topic_selected(self, message: TopicList.Selected):
        logging.info(message)

    def on_mount(self):
        label = self.query_one("#topic")
        label.border_title = "Topics"
        label.border_subtitle = "status"
        self.panel.styles.color = Color(191, 78, 96)

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        self.panel = ScrollableContainer(TopicPanel(), id="topic", classes="box")
        yield Header()
        yield self.panel
        yield TopicDetails(classes="box").data_bind(TopicPanelApp.topic_details)
        yield Footer()

app = TopicPanelApp()

if __name__ == "__main__":
    app = TopicPanelApp()
    app.run()
