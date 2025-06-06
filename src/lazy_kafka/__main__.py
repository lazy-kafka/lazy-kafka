from __future__ import annotations

import logging
import sys
from functools import cached_property
from pathlib import Path
from lazy_kafka._logging import configure_base_logger
configure_base_logger()

from rich.text import Text
from textual.app import App, ComposeResult
from textual.css.query import NoMatches
from textual.screen import Screen
from textual.widgets import (
    Footer,
    Header,
    Label,
    Pretty,
    Tab,
    Tabs,
)

# services
from lazy_kafka import connect, registry, topic
from lazy_kafka.config import Configuration
from lazy_kafka.theme import frog_theme
from lazy_kafka.widgets.kconnect import KConnectPanel
from lazy_kafka.widgets.registry import SchemaRegistryPanel
from lazy_kafka.widgets.switcher import ContentSwitcher
from lazy_kafka.widgets.topic import TopicPanel

class SettingsScreen(Screen):
    """Screen to display settings."""

    def compose(self) -> ComposeResult:
        assert self.app.lazy_kafka_config
        yield Label("Default configuration file: ")
        yield Label(f"  [yellow]{self.app._configuration_file.absolute()}[/]")
        yield Pretty(self.app.lazy_kafka_config)
        yield Footer()


class DashboardScreen(Screen):
    """Content screens."""

    BINDINGS = [
        ("l", "next_tab", "Next"),
        ("h", "previous_tab", "Previous"),
    ]

    def action_next_tab(self):
        self.query_one("#tabs", Tabs).action_next_tab()

    def action_previous_tab(self):
        self.query_one("#tabs", Tabs).action_previous_tab()

    def compose(self) -> ComposeResult:
        assert hasattr(self.app, "lazy_kafka_config"), "Application failed to load configuration."

        yield Header()

        yield Tabs(
            # TODO: these widgets should be lazy mounted so e.g.: load_data only runs when they are first visited by the user.
            Tab("Topic", id="tab-topic"),
            Tab("Schema Registry", id="tab-schema"),
            Tab(Text.from_markup(":warning: K-connect"), id="tab-connect"),
            id="tabs",
        )
        with ContentSwitcher(initial="topic", id="main-content-switcher"):
            try:
                _hook = topic.KafkaClient(
                    self.app.lazy_kafka_config.kafka
                )
            except (ConnectionRefusedError, AssertionError):
                _hook = None
                yield Label("Error", id="tab-topic")
            if _hook is not None:
                yield TopicPanel(id="tab-topic", classes="has-border", hook = _hook)

            try:
                _hook = registry.SchemaRegistry(
                    self.app.lazy_kafka_config.registry
                )
            except ConnectionRefusedError:
                _hook = None
                yield Label("Error", id="tab-schema")
            if _hook is not None:
                yield SchemaRegistryPanel(id="tab-schema", classes="has-border", hook=_hook)

            try:
                _hook = connect.Connect(
                    self.app.lazy_kafka_config.connect
                )
            except ConnectionRefusedError:
                _hook = None
                yield Label("Error", id="tab-connect")
            if _hook is not None:
                # TODO: if hook is None, the widget should be just a Label?
                yield KConnectPanel(id="tab-connect", classes="has-border", hook = _hook)
        yield Footer(show_command_palette=False)

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """Handle TabActivated message sent by Tabs.

        Tab activated handler customized to focus the DataTable component of
        the current tab (this saves a 'Tab' key press).
        """
        cs: ContentSwitcher = self.query_one("#main-content-switcher")
        cs.current = event.tab.id
        if cs.visible_content is None:
            return
        try:
            self.set_focus(cs.visible_content)
        except NoMatches:
            logging.error("No DataTable component in %s", event.tab.id)


class LazyKafka(App[None]):
    """A Textual app to browse kafka related stuff'n such."""

    BINDINGS = [
        ("d", "switch_mode('dashboard')", "Dashboard"),
        ("s", "switch_mode('settings')", "Settings"),
        ("h", "switch_mode('help')", "Help"),
    ]
    MODES = {
        "dashboard": DashboardScreen,
        "settings": SettingsScreen,
    }

    CSS_PATH = "style.tcss"

    def __init__(
        self,
        driver_class: Type[Driver] | None = None,
        css_path: CSSPathType | None = None,
        watch_css: bool = False,
        ansi_color: bool = False,
    ):
        self.lazy_kafka_config = Configuration.from_local_config()
        super().__init__(driver_class, css_path, watch_css, ansi_color)

    @cached_property
    def _configuration_file(self) -> Path:
        return self.lazy_kafka_config._file

    def on_load(self):
        """Load action before anything visible happens."""
        logging.debug("Configuration file: %s", self._configuration_file)
        self.lazy_kafka_config = Configuration.from_toml(self._configuration_file)
        logging.debug("app config: %s", f"{self.lazy_kafka_config}")

    def on_mount(self) -> None:
        self.register_theme(frog_theme)
        self.theme = "frog"
        self.switch_mode("dashboard")


app = LazyKafka()

if __name__ == "__main__":
# TODO: config will have to be read earlier so the CLI can handle it.
#    _cfg = Configuration.from_local_config().registry
#    logging.debug("%s", _cfg)
#    _hook = registry.SchemaRegistry(
#        _cfg
#    )
    if len(sys.argv) <= 1:
        app = LazyKafka()
        app.run()
    else:
        from lazy_kafka.cli import app

        app()
