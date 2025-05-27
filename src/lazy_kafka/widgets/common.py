from __future__ import annotations

import logging
from abc import abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Mapping,
    Protocol,
    Sequence,
    TypeVar,
    Union,
)

from textual import work
from textual.binding import Binding
from textual.containers import Container, ScrollableContainer
from textual.css.query import NoMatches
from textual.message import Message
from textual.widget import Widget
from textual.widgets import DataTable, Input, Label, Pretty
from textual.widgets.data_table import DuplicateKey, RowDoesNotExist

from lazy_kafka.utils import get_current_time

if TYPE_CHECKING:
    from lazy_kafka.types import ProviderProtocol, StrLike

logging.basicConfig(level=logging.INFO)

_LOGGER = logging.getLogger(__name__)

class CanConvertToTable(Protocol):
    def to_table_values(self) -> Sequence[Any]:
        ...

T = TypeVar("T", bound=Union[str, None])
"""Used for the DataTable content and HashMap keys."""

S = TypeVar("S", bound=CanConvertToTable)
"""Used for Details content and HashMap values."""


class SubjectDetails(Widget):
    """Display subject details next to the main table."""

    DEFAULT_CSS = """
      SubjectDetails {
        layer: below;
        align-vertical:bottom;
        ScrollableContainer {
          layout: vertical;
          width: 1fr;
          height: auto;
          Pretty {
            color: $secondary;
          }
        }
        width: 1fr;
      }
    """
    def compose(self):
        yield ScrollableContainer(
                Pretty([]),
            )

    def on_mount(self):
        self.query_one(ScrollableContainer).border_subtitle = "Details"


class WidgetWithDataTable(Generic[T,S], Container, can_focus=True):
    """Template class for core widgets with a DataTable and Details.

    The class is generic over:
        `T` - the type used for the `DataTable` content
        `S` - the type used for the `details`

    Messages:
        Selected: emitted on new item selected from data table

    Instance members:
        subjects: a Mapping[str,S] or Mapping[T,S] used as store

    Reactive members:
       selected_id: currently selected id (see Messages)
       details: more displayable information about subject corresponding to selected_id

    """

    BINDINGS = [
        ("j", "next_widget_item", "↓"),
        ("k", "previous_widget_item", "↑"),
        ("f", "toggle_refresh", "Toggle follow"),
        # TODO: remove ("escape", "unset_topic", "close"),
        Binding("slash", "search_subject", "Search", False),
    ]
    DEFAULT_CSS = """
    WidgetWithDataTable {
      layout: vertical;
      max-height: 90%;
      DataTable {
        width: 2fr;
        background: $surface;
        & > .datatable--header {
          background: transparent;
          color: $primary;
          text-style: bold;
        }

        & > .datatable--odd-row {
          background: $surface-lighten-1;
        }

        & > .datatable--even-row {
          background: $background;
        }

        .datatable--cursor {
          color: $secondary;
          background: $primary-lighten-3;
          text-style: bold;
        }
      }
    }
    """

    hook: ProviderProtocol[T,S]
    subjects: Mapping[T,S]

    def __init__(self, *args, **kwargs):
        assert self.hook is not None
        assert self.subjects is not None
        assert self.data_auto_refresh is not None
        super().__init__(*args, **kwargs)

    class Selected(Message):
        """Color selected message."""

        def __init__(self, selected_id: T) -> None:
            self.selected_id = selected_id
            super().__init__()

    def action_next_widget_item(self):
        self.query_one(DataTable).action_cursor_down()

    def action_previous_widget_item(self):
        self.query_one(DataTable).action_cursor_up()

    def action_stop_refresh(self):
        self.update_timer.pause()
        label = self.query_one("#icon", Label)
        label.remove_class("-live")
        self.data_auto_refresh = False

    def action_start_refresh(self):
        self.update_timer.resume()
        label = self.query_one("#icon", Label)
        label.add_class("-live")
        self.data_auto_refresh = True

    def action_toggle_refresh(self):
        if self.data_auto_refresh:
            self.action_stop_refresh()
        else:
            self.action_start_refresh()

    async def action_search_subject(self) -> None:
        try:
            res = self.query_one(Input)
            await res.remove()
        except NoMatches:
            res = await self.mount(
                Input(placeholder="Search..."), before=self.query_one(DataTable)
            )
            res = self.query_one(Input)
            self.app.set_focus(res)

    def on_mount(self):
        _LOGGER.debug("HERE IN PARENT mount")
        self.update_timer = self.set_interval(2, self.action_load_data, pause=True)

    def on_input_changed(self, event: Input.Changed) -> None:
        logging.debug(event)
        token = event.value
        table = self.query_one(DataTable)
        table.loading = True
        table.clear()
        _rows = {
            k: v.replace(token, f"[dark_orange]{token}[/dark_orange]")
            for k, v in self.subjects.items()
            if token in v.lower()
        }
        for k, v in _rows.items():
            table.add_row(v, key=k)

        table.loading = False

    def on_data_table_focused(self, event):
        _LOGGER.debug("DATA TABLE FOC %s", f"{event!r}")


    def watch_details(self, details: str):
        """Callback on topic changed."""
        try:
            details_panel = self.query_one(Pretty)
        except NoMatches as _:
            details_panel = SubjectDetails(id="details", classes="has-border")
            self.mount(details_panel)
            return
        self.query_one(Pretty).update(details)
        self.log(f"{details}")

    async def action_load_data(self):
        data_table = self.query_one(DataTable)
        self.load_data(data_table, display_load=False)

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        # The post_message method sends an event to be handled in the DOM
        _LOGGER.debug(f"selected: {event}")
        if event.row_key.value is None:
            _LOGGER.error("False event")
            return
        try:
            _LOGGER.debug(f"{self.subjects=}")
            _LOGGER.debug(f"{event.row_key.value=}")
            self.post_message(self.Selected(self.subjects[event.row_key.value]))
        except KeyError as e:
            _LOGGER.error("Something went wrong.", exc_info=e)

    @work(exclusive=True, exit_on_error=False)
    async def on_widget_with_data_table_selected(
        self, message: WidgetWithDataTable.Selected
    ) -> None:
        """Set the selected_id attribute and fetch details.

        Currently -> Message() -> Reactive() -> watch_topic()
        """
        _LOGGER.debug(f"Row highlihghted{message.selected_id=}")
        # Note, this should be in the init method ...
        self.selected_id = message.selected_id
        self.details = await self.hook.aget_details(message.selected_id)
        _LOGGER.debug(self.details)

    async def on_focus(self, event):
        """Perform a single refresh on focus."""
        for data_table in self.query(DataTable):
            self.load_data(data_table)

    @work(exclusive=True)
    async def load_data(self, data_table: DataTable, display_load=True) -> None:
        """Load data.

        Args:
            display_load (bool): set to false to disable loading animation.
            data_table: DataTable instance to be updated.
        """
        data_table.loading = display_load
        _response = await self.hook.asubjects()
        self.subjects = self.subject_to_table(_response)
        # For now, clearing the whole table looks viable...
        # problem is that it resets the highlighted row - annoying
        _LOGGER.debug(f"self.subjects is None: {self.subjects is None}")
        for k,v in self.subjects.items():
            try:
                data_table.add_row(*v.to_table_values(), key=k)
            except DuplicateKey:
                # No details are shown in rows, so it's ok to just pass
                continue
        # Set the cursor to the same row
        # TODO: emit data-loaded event and react to that with "move_cursor"
        try:
            _new_index_of_old_row = data_table.get_row_index(self.selected_id)
        except RowDoesNotExist:
            _new_index_of_old_row = None
        if _new_index_of_old_row:
            data_table.move_cursor(row=_new_index_of_old_row)

        data_table.loading = False
        label = self.query_one("#time", Label)
        label.update(f"{get_current_time()}")

    @abstractmethod
    def subject_to_table(self, *args, **kwargs) -> Mapping[StrLike, S]:
        ...

