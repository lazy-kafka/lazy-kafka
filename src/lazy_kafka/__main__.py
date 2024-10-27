from __future__ import annotations

import logging
from typing import Self

import rich.console
import textual
from pathlib import Path
from rich.text import Text
from textual.app import App, ComposeResult
from textual.css.query import NoMatches
from textual.logging import TextualHandler
from textual.reactive import Reactive, reactive
from textual.widget import Widget
from textual.widgets import (
    Footer,
    Header,
    Tab,
    Tabs,
)

from lazy_kafka.config import Configuration
from lazy_kafka.connect import ConnectorData
from lazy_kafka.widgets.kconnect import KConnectPanel
from lazy_kafka.widgets.registry import SchemaRegistryPanel
from lazy_kafka.widgets.switcher import ContentSwitcher
from lazy_kafka.widgets.topic import TopicPanel

logging.basicConfig(level="NOTSET", handlers=[TextualHandler()])

CONSOLE = rich.console.Console()
print(textual.__version__)


class ConnectorDetails(Widget):
    connector = reactive("")

    def render(self) -> str:
        return f"[b]CONNECTOR:[/b] {self.connector}"


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


# TODO: Modes will be used for settings and help screen, which are global
#           maybe screens and mode_switch are better suited
#           ref: https://textual.textualize.io/guide/screens/#modes


class LazyKafka(App[None]):
    """A Textual app to browse kafka related stuff'n such."""

    #    topic: Reactive[TopicData] = reactive(TopicData())
    connector: Reactive[ConnectorData] = reactive(ConnectorData())

    CSS_PATH = "style.tcss"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("l", "next_tab", "Next"),
        ("h", "previous_tab", "Previous"),
    ]

    def __init__(
        self,
        driver_class: Type[Driver] | None = None,
        css_path: CSSPathType | None = None,
        watch_css: bool = False,
        ansi_color: bool = False,
    ):
        self.lazy_kafka_config = Configuration()
        super().__init__(driver_class, css_path, watch_css, ansi_color)

    def on_load(self):
        """Load action before anything visible happens."""
        logging.critical("HERE")
        _p = Path(__file__).parent / "default_config.toml"
        self.lazy_kafka_config = Configuration.from_toml(_p)
        logging.debug(f"app config: {self.lazy_kafka_config}")

    def on_mount(self):
        pass

    def action_next_tab(self):
        self.query_one("#tabs").action_next_tab()

    def action_previous_tab(self):
        self.query_one("#tabs").action_previous_tab()

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        yield Header()

        yield Tabs(
            Tab("Kafka", id="topic"),
            Tab("Schema Registry", id="tab-schema"),
            Tab(Text.from_markup(":warning: K-connect"), id="tab-connect"),
            id="tabs",
        )
        with ContentSwitcher(initial="topic", id="main-content-switcher"):
            yield TopicPanel(id="topic", classes="box")
            yield SchemaRegistryPanel(id="tab-schema")
            yield KConnectPanel(id="tab-connect")
        yield Footer()

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """Handle TabActivated message sent by Tabs.

        Tab activated handler customized to focus the DataTable component of
        the current tab (this saves a 'Tab' key press).
        """
        logging.debug("tab actinvated: %s", f"{event!r}")
        logging.debug("tab : %s", f"{event.tab!r}")
        cs: ContentSwitcher = self.query_one("#main-content-switcher")
        cs.current = event.tab.id
        if cs.visible_content is None:
            return
        try:
            self.set_focus(cs.visible_content)
        except NoMatches:
            logging.error("No DataTable component in %s", event.tab.id)

    def on_schema_registry_panel_dialog_open(
        self, message: SchemaRegistryPanel.DialogOpen
    ):
        logging.debug("------------------------------")
        logging.debug(message)
        d = self.query_one(message.selected_id)
        logging.debug(f"found {d}")
        logging.debug(f"focused {self.focused}")
        self.set_focus(d)
        logging.debug(f"focused after {self.focused}")


app = LazyKafka()

if __name__ == "__main__":
    app = LazyKafka()
    app.run()
