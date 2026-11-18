from __future__ import annotations

from textual.widget import Widget

from lazy_kafka.__main__ import LazyKafka
from lazy_kafka.widgets._logs import LogsWidget
from lazy_kafka.widgets.common import (
    DataTableCursorMixin,
    DetailsPanelMixin,
    SubjectDetails,
)


async def test_app_runs_headless():
    app = LazyKafka()
    async with app.run_test(size=(100, 40)) as pilot:
        await pilot.pause()
        assert app.is_running
        # dashboard mode should be active after on_mount
        assert app.screen is not None
        tabs = app.screen.query_one("#tabs")
        assert tabs is not None


async def test_keyboard_bindings_headless():
    app = LazyKafka()
    async with app.run_test(size=(100, 40)) as pilot:
        await pilot.pause()
        await pilot.press("s")  # switch to settings mode
        await pilot.pause()
        assert app.screen.__class__.__name__ == "SettingsScreen"


async def test_logs_screen_headless():
    """Pressing L must switch to the logs screen without raising (# set_focus)."""
    app = LazyKafka()
    async with app.run_test(size=(100, 40)) as pilot:
        await pilot.pause()
        await pilot.press("L")
        await pilot.pause()
        assert app.screen.__class__.__name__ == "LogsScreen"
        logs_widget = app.screen.query_one("LogsWidget")
        # the DataTable should have received focus from LogsWidget.on_mount
        assert app.focused is logs_widget.query_one("#logs-table")
        # exactly one footer, like the settings screen (regression: the
        # widget used to yield its own Footer, doubling the docked bar)
        from textual.widgets import Footer

        assert len(app.screen.query(Footer)) == 1


def test_logs_widget_reuses_common_mechanisms():
    """Logs table shares the vim-cursor and details-panel code with topic screens."""
    assert issubclass(LogsWidget, DataTableCursorMixin)
    assert issubclass(LogsWidget, DetailsPanelMixin)
    assert issubclass(SubjectDetails, Widget)
    assert DataTableCursorMixin.action_next_widget_item is not None


async def test_logs_zebra_vim_nav_and_details():
    """Logs table matches other screens: zebra rows, j/k navigation, and a
    bordered bottom panel with the selected message untruncated."""
    import logging as pylog

    from textual.widgets import DataTable

    long_message = "L" * 500
    app = LazyKafka()
    handler = app.log_handler
    handler.emit(pylog.LogRecord("x", pylog.INFO, "f", 1, "first message", (), None))
    handler.emit(pylog.LogRecord("x", pylog.WARNING, "f", 1, long_message, (), None))

    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.press("L")
        await pilot.pause()
        table = app.screen.query_one("#logs-table", DataTable)
        assert table.zebra_stripes
        assert table.cursor_type == "row"
        assert table.row_count == 2

        # frame + black background, like the topic/message tables
        from textual.color import Color

        logs_widget = app.screen.query_one("LogsWidget")
        assert "has-border" in logs_widget.classes
        assert logs_widget.styles.border.top[0] == "round"
        assert table.styles.background == Color(0, 0, 0)

        await pilot.press("j")  # cursor down: row 0 -> 1
        await pilot.pause()
        await pilot.pause()
        assert table.cursor_row == 1

        # details panel docked at the bottom shows the full message
        details_panel = app.screen.query_one("SubjectDetails")
        assert details_panel.shown_details == long_message

        await pilot.press("k")  # cursor up: row 1 -> 0
        await pilot.pause()
        await pilot.pause()
        assert table.cursor_row == 0
        assert details_panel.shown_details == "first message"


async def test_log_handler_captures_without_console_output(capsys):
    """Reproduce main()'s logging setup: all records go to the LogHandler,
    and nothing is written to stdout/stderr."""
    import logging

    from lazy_kafka.widgets._logs import LogHandler

    handler = LogHandler()
    logging.basicConfig(level="NOTSET", handlers=[handler], force=True)
    try:
        logging.getLogger().setLevel("NOTSET")
        logging.getLogger("lazy_kafka.config").debug("Configfile path: /tmp/x.toml")
        logging.getLogger("lazy_kafka.config").info("hello")

        out, err = capsys.readouterr()
        assert out == ""
        assert err == ""
        levels = [entry.level for entry in handler.get_entries()]
        assert levels == ["DEBUG", "INFO"]
    finally:
        logging.getLogger().handlers.clear()

