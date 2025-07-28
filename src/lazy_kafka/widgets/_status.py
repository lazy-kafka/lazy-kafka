"""Status line widget."""

from __future__ import annotations

import logging

from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import (
    Label,
)

_LOGGER = logging.getLogger(__name__)


class Status(Widget, can_focus=False):
    """Display a greeting.

    The symbol is:
        ⬤ BLACK LARGE CIRCLE 2B24
    alternative:
        ● BLACK CIRCLE 25CF
    """

    DEFAULT_CSS = """
    Status {
        height: 1;
    }
    """

    def compose(self):
        yield Horizontal(
            Label(" ⬤ ", id="icon", classes="status-text"),
            Label("[i]Updated:[/] ", id="text"),
            Label("--:--:--", id="time", classes="status-text"),
        )
