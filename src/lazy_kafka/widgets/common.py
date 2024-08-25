from __future__ import annotations

import logging

from textual.containers import Container, ScrollableContainer
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget

logging.basicConfig(level=logging.INFO)

_LOGGER = logging.getLogger(__name__)

class MyContainer(Container, can_focus=True):
    """Class which all plugins should stem from."""

    def on_focus(self):
        _LOGGER.debug("heeeyaho")

    def action_unset_topic(self) -> None:
        """Called to remove a timer."""
        try:
            topic_details = self.query_one("#details")
        except NoMatches:
            return
        topic_details.remove()

class MyScrollableContainer(ScrollableContainer):
    """Used for the details panel"""
    class Completed(Message):
        """Color selected message."""

        def __init__(self) -> None:
            _LOGGER.debug("%s Mounted", self.__class__)
            self.done = True
            super().__init__()

    def on_focus(self) -> None:
        _LOGGER.debug("HERE")

    def on_mount(self) -> None:
        def comp():
            self.post_message(self.Completed())

        self.styles.animate(
            "width", value=30.0, duration=1.0, easing="out_expo", on_complete=comp
        )


class Details(Widget):
    detail_name = reactive("")

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = "details-content",
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )

