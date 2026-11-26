from __future__ import annotations

import logging
from abc import abstractmethod
from collections.abc import Mapping, Sequence
from dataclasses import astuple, is_dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Protocol,
)

from rich.markup import escape
from textual import work
from textual.binding import Binding
from textual.containers import Container, ScrollableContainer
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import Reactive, reactive
from textual.widget import Widget
from textual.widgets import DataTable, Input, Label, Pretty
from textual.widgets.data_table import DuplicateKey, RowDoesNotExist

from lazy_kafka.utils import get_current_time

if TYPE_CHECKING:
    from lazy_kafka._types import ProviderProtocol, StrLike_co

_LOGGER = logging.getLogger(__name__)


class CanConvertToTable(Protocol):
    """Anything that can convert itself to table row values."""

    def to_table_values(self) -> Sequence[Any]: ...


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

    def show(self, details: Any) -> None:
        """Update the displayed details."""
        self.shown_details = details
        self.query_one(Pretty).update(details)


class DataTableCursorMixin:
    """Vim-style j/k cursor navigation over the first child `DataTable`."""

    def action_next_widget_item(self):
        self.query_one(DataTable).action_cursor_down()

    def action_previous_widget_item(self):
        self.query_one(DataTable).action_cursor_up()


class DetailsPanelMixin:
    """Display `details` in a bordered `SubjectDetails` panel docked at the bottom.

    Expects a reactive `details` attribute; mounting the panel is delayed to
    the moment details are first set.
    """

    details: Reactive[Any] = reactive(None, init=False)

    def watch_details(self, details: Any) -> None:
        """Handle a change of the details."""
        try:
            details_panel = self.query_one(SubjectDetails)
        except NoMatches:
            details_panel = SubjectDetails(id="details", classes="has-border")
            self.mount(details_panel)
            self.call_after_refresh(details_panel.show, details)
            return
        details_panel.show(details)


class SearchInput(Input):
    """Standard input used by the search filters."""

    # def on_input_submitted(self, message: Input.Submitted):
    # self.log.info(f"Hello {message}")


class WidgetWithDataTable[T: str | None, S: CanConvertToTable](
    DataTableCursorMixin, DetailsPanelMixin, Container, can_focus=True
):
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
       filter_token: a filter expression to limit the subjects on display

    """

    BINDINGS: ClassVar[list] = [
        ("j", "next_widget_item", "↓"),
        ("k", "previous_widget_item", "↑"),
        ("f", "toggle_refresh", "Toggle follow"),
        # TODO: remove ("escape", "unset_topic", "close"),
        Binding(
            "slash",
            "search_subject",
            "Search",
            show=True,
            key_display="/",
            tooltip="Search by name",
        ),
    ]
    DEFAULT_CSS = """
    WidgetWithDataTable {
      layout: vertical;
      height: 1fr;
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

    hook: ProviderProtocol[T, S]
    subjects: Mapping[T, S]
    filter_token: Reactive[str] = reactive("")
    """Applied on Enter: rows not matching are dropped from the table."""

    search_token: Reactive[str] = reactive("")
    """Live search term: matches are highlighted while typing (no filtering)."""

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
        """Toggle the search bar (`/` binding).

        Closing the bar (mounting it again over an existing one) resets the
        applied filter, so the next search starts from a clean slate.
        """
        try:
            res = self.query_one(SearchInput)
        except NoMatches:
            self.mount(
                SearchInput(placeholder="Search..."), before=self.query_one(DataTable)
            )
            self.query_one(SearchInput).focus()
            return
        await res.remove()
        self._reset_search_and_filter(focus_table=True)

    def on_input_submitted(self, message: Input.Submitted) -> None:
        """Enter: filter rows to matches; Enter on an empty bar resets."""
        value = message.value
        if value == "":
            self._reset_search_and_filter(focus_table=True)
        else:
            self.filter_token = value
            self.query_one(DataTable).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Live search: highlight matching cells while typing (no filtering)."""
        self.search_token = event.value

    def watch_filter_token(self) -> None:
        """Re-populate the table when a filter is (un)applied."""
        self._update_border_title()
        self._refresh_table()

    def watch_search_token(self) -> None:
        """Highlight matches live while typing and reflect the term in the title."""
        self._update_border_title()
        self._refresh_table()

    # --- Search/filter internals ------------------------------------------

    def _reset_search_and_filter(self, *, focus_table: bool = True) -> None:
        """Clear search highlight and applied filter; restore the title."""
        self.search_token = ""
        # Guard lets the reactive skip a no-op watcher cycle when untouched.
        if self.filter_token:
            self.filter_token = ""
        if focus_table:
            self.focus()

    def _matchable_strings(self, data: Any) -> Sequence[str]:
        """Flatten a row value into plain strings for search matching."""
        if is_dataclass(data) and not isinstance(data, type):
            return [str(v) for v in astuple(data)]
        return [str(data)]

    def _visible_rows(self) -> dict:
        """Compute displayed rows: apply the filter, then the search highlight.

        - `filter_token` (Enter) drops non-matching rows.
        - `search_token` (typing) re-uses the subclass `apply_filter` to
          highlight matching substrings (e.g. `dark_orange`) without dropping
          anything.
        """
        rows: dict = self.subjects
        if self.filter_token:
            token = self.filter_token.lower()
            rows = {
                k: v
                for k, v in rows.items()
                if any(token in s.lower() for s in self._matchable_strings(v))
            }
        if self.search_token:
            rows = {k: self.apply_filter(v, self.search_token) for k, v in rows.items()}
        return rows

    def _populate_rows(self, table: DataTable) -> None:
        """Rebuild table rows from `_visible_rows`, preserving the cursor."""
        # Snapshot the currently highlighted row key so the cursor can follow
        # the same row across rebuilds (fall back to the last selection).
        try:
            row_key = table.coordinate_to_cell_key(
                table.cursor_coordinate
            ).row_key.value
        except Exception:  # noqa: BLE001 - empty table / no cursor yet
            row_key = None
        row_key = (
            row_key if row_key is not None else getattr(self, "selected_id", None)
        )  # `selected_id` is declared per subclass

        table.clear()
        for k, v in self._visible_rows().items():
            try:
                table.add_row(*v, key=k)
            except DuplicateKey:
                # No details are shown in rows, so it's ok to just pass
                continue

        if row_key is not None:
            try:
                table.move_cursor(row=table.get_row_index(row_key))
            except RowDoesNotExist:
                pass

    def _refresh_table(self) -> None:
        try:
            table = self.query_one(DataTable)
        except NoMatches:  # not mounted yet
            return
        table.loading = True
        self._populate_rows(table)
        table.loading = False

    def _update_border_title(self) -> None:
        """Append the live search term to the container's border title."""
        if self._base_border_title is None:
            self._base_border_title = self.border_title or self.BORDER_TITLE
        term = self.search_token or self.filter_token
        if term:
            self.border_title = (
                f"{self._base_border_title} [dim]\\⌕[/] [bold]{escape(term)}[/bold]"
            )
        else:
            self.border_title = self._base_border_title

    _base_border_title: str | None = None

    def on_mount(self):
        self.update_timer = self.set_interval(2, self.action_load_data, pause=True)

    def on_data_table_focused(self, event):
        _LOGGER.debug("DATA TABLE FOC %s", f"{event!r}")

    async def action_load_data(self):
        data_table = self.query_one(DataTable)
        self.load_data(data_table, display_load=False)

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        # The post_message method sends an event to be handled in the DOM
        _LOGGER.debug("selected: %s", event)
        if event.cursor_row == -1:
            # Already in top row
            return
        if event.row_key.value is None:
            _LOGGER.error("False event")
            return
        try:
            _LOGGER.debug("subjects=%r", self.subjects)
            _LOGGER.debug("event.row_key.value=%r", event.row_key.value)
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
        _LOGGER.debug("Row highlihghted selected_id=%r", message.selected_id)
        # Note, this should be in the init method ...
        self.selected_id = message.selected_id
        self.details = await self.hook.aget_details(message.selected_id)
        _LOGGER.debug("details=%r", self.details)

        # TODO: it's a bit too much to refresh on focus?

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
        _LOGGER.debug("self.subjects is None: %s", self.subjects is None)
        # Row population applies the active filter/search state and keeps the
        # cursor on the same row across rebuilds.
        self._populate_rows(data_table)
        # TODO: emit data-loaded event and react to that with "move_cursor"

        data_table.loading = False
        label = self.query_one("#time", Label)
        label.update(f"{get_current_time()}")

    @abstractmethod
    def subject_to_table(self, *args, **kwargs) -> Mapping[StrLike_co, S]: ...

    @abstractmethod
    def apply_filter(self, data: T, token: str) -> T: ...
