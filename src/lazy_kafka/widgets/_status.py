"""Status line widget."""

from __future__ import annotations

import logging

from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import (
    Label,
)

logging.basicConfig(level=logging.INFO)

_LOGGER = logging.getLogger(__name__)


class Status(Widget, can_focus=False):
    """Display a greeting.

    # use U+23FA
    """

    DEFAULT_CSS = """
    Status {
        height: 1;
    }
    """

    def compose(self):
        yield Horizontal(
            Label("⏺ ", id="icon", classes="status-text"),
            Label("[i]Updated:[/] ", id="text"),
            Label("--:--:--", id="time", classes="status-text"),
        )
