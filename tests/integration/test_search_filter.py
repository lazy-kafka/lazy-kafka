"""Integration tests for the search/filter behavior of WidgetWithDataTable.

Behavior under test:
- typing (`/` then characters): live highlight of matching cells, NO row
  filtering, term appended to the border title;
- Enter: rows not matching are dropped (filter applied);
- Enter on an empty search bar (or `/` toggle-close): full reset — highlight
  and filter cleared, title restored.
"""

from __future__ import annotations

from typing import NamedTuple

from textual.app import App, ComposeResult
from textual.widgets import DataTable, Label

from lazy_kafka.widgets.common import SearchInput, WidgetWithDataTable


class Row(NamedTuple):
    """One display row (a single cell)."""

    name: str


class FakeHook:
    """Minimal provider: returns a fixed list of rows."""

    def __init__(self, rows: list[str]) -> None:
        self._rows = rows

    async def asubjects(self) -> list[str]:
        return list(self._rows)


class FakeFilterMixin(WidgetWithDataTable[str, Row]):
    """Untitled-table widget fed by FakeHook — all styling via apply_filter."""

    def __init__(self, rows: list[str], **kwargs) -> None:
        self.hook = FakeHook(rows)
        self.subjects = dict()
        self.data_auto_refresh = False
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        yield Label(id="time")
        yield DataTable(cursor_type="row", zebra_stripes=True)

    def on_mount(self) -> None:
        self.query_one(DataTable).add_column("Name")
        super().on_mount()
        self.load_data(self.query_one(DataTable))

    def subject_to_table(self, response: list[str], *args, **kwargs) -> dict[str, Row]:
        return {name: Row(name) for name in response}

    def apply_filter(self, data: Row, token: str) -> Row:
        return Row(data.name.replace(token, f"[dark_orange]{token}[/dark_orange]"))


class SearchApp(App):
    def compose(self) -> ComposeResult:
        yield FakeFilterMixin(rows=["alpha", "alphabet", "beta", "gamma"])


def _panel(app: SearchApp) -> FakeFilterMixin:
    return app.screen.query_one(FakeFilterMixin)


def _table(app: SearchApp) -> DataTable:
    return app.screen.query_one(DataTable)


async def test_typing_highlights_all_rows_kept_and_title_updated():
    app = SearchApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.press("slash")
        assert app.screen.query_one(SearchInput)

        await pilot.press(*"alp")
        await pilot.pause()
        panel, table = _panel(app), _table(app)

        # Live search only: nothing is filtered away.
        assert panel.search_token == "alp"
        assert panel.filter_token == ""
        assert table.row_count == 4
        # Matches are highlighted in-place…
        assert "[dark_orange]alp[/dark_orange]" in str(table.get_row("alpha"))
        # …non-matching rows are left untouched.
        assert "[dark_orange]" not in str(table.get_row("beta"))
        # Term is appended to the container title.
        assert "alp" in panel.border_title


async def test_enter_filters_rows_to_matches():
    app = SearchApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.press("slash", *"alp", "enter")
        await pilot.pause()
        panel, table = _panel(app), _table(app)

        assert panel.filter_token == "alp"
        # Only alpha and alphabet survive the filter.
        assert table.row_count == 2
        # Focus is handed back to the table.
        assert table.has_focus or panel.has_focus


async def test_enter_on_empty_search_resets_and_restores_title():
    app = SearchApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.press("slash", *"alp", "enter")
        await pilot.pause()
        panel = _panel(app)
        assert panel.filter_token == "alp"  # precondition: filter active

        # Re-open the (empty this time) search bar, then Enter on empty.
        await pilot.press("slash", "enter")
        await pilot.pause()
        table = _table(app)

        assert panel.search_token == ""
        assert panel.filter_token == ""
        # All rows are visible again…
        assert table.row_count == 4
        # …highlight markup is gone…
        assert "[dark_orange]" not in str(table.get_row("beta"))
        # …and the title no longer shows the term.
        assert "alp" not in panel.border_title


async def test_toggle_search_bar_off_resets():
    app = SearchApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.press("slash", *"alp", "enter")
        await pilot.pause()
        panel = _panel(app)
        assert panel.filter_token == "alp"  # precondition: filter active

        # `/` again closes the bar and resets.
        await pilot.press("slash")
        await pilot.pause()
        table = _table(app)

        assert panel.search_token == ""
        assert panel.filter_token == ""
        assert table.row_count == 4
