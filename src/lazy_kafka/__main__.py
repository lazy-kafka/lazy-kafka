from __future__ import annotations

import logging
import sys
from functools import cached_property
from pathlib import Path

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

from lazy_kafka.config import Configuration
from lazy_kafka.plugin import iter_plugins, load_builtin_plugins
from lazy_kafka.theme import frog_theme
from lazy_kafka.widgets.switcher import ContentSwitcher


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
        ("l", "next_tab", "→"),
        ("h", "previous_tab", "←"),
    ]

    def action_next_tab(self):
        self.query_one("#tabs", Tabs).action_next_tab()

    def action_previous_tab(self):
        self.query_one("#tabs", Tabs).action_previous_tab()

    def compose(self) -> ComposeResult:
        assert hasattr(self.app, "lazy_kafka_config"), (
            "Application failed to load configuration."
        )

        yield Header()

        plugins = list(iter_plugins())
        # TODO: panels should be lazy-mounted so their load_data only runs when
        # a tab is first visited by the user.
        yield Tabs(
            *(Tab(p.tab_label, id=p.tab_id) for p in plugins),
            id="tabs",
        )
        initial = plugins[0].tab_id if plugins else None
        with ContentSwitcher(initial=initial, id="main-content-switcher"):
            for plugin in plugins:
                result = plugin.build_panel(self.app.lazy_kafka_config)
                yield Label(result, id=plugin.tab_id) if isinstance(result, str) else result
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
        load_builtin_plugins()
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


def main():
    """Main entrypoint to the TUI and CLI."""
    if len(sys.argv) <= 1:
        from textual.logging import TextualHandler

        logging.basicConfig(
            level="NOTSET",
            handlers=[TextualHandler()],
        )

        app = LazyKafka()
        app.run()
    else:
        from lazy_kafka.cli import app

        app()


if __name__ == "__main__":
    main()
