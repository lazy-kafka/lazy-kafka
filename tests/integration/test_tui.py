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


async def test_logs_vim_jump_keys():
    """G jumps to the newest entry, gg to the oldest (standard vim)."""
    import logging as pylog

    app = LazyKafka()
    handler = app.log_handler
    for i in range(50):
        handler.emit(pylog.LogRecord("x", pylog.INFO, "f", 1, f"entry {i}", (), None))

    async with app.run_test(size=(120, 20)) as pilot:
        await pilot.press("L")
        await pilot.pause()
        table = app.screen.query_one("#logs-table")

        await pilot.press("g", "g")
        await pilot.pause()
        assert table.cursor_row == 0

        # a rebuild must not yank the cursor away from the top
        handler.emit(pylog.LogRecord("x", pylog.INFO, "f", 1, "new entry", (), None))
        await pilot.pause(0.2)
        assert table.cursor_row == 0

        await pilot.press("G")
        await pilot.pause()
        assert table.cursor_row == table.row_count - 1

        # a rebuild must not yank the cursor away from the bottom
        handler.emit(pylog.LogRecord("x", pylog.INFO, "f", 1, "newer entry", (), None))
        await pilot.pause(0.2)
        assert table.cursor_row == table.row_count - 1

        # gg returns to the oldest entry
        await pilot.press("g", "g")
        await pilot.pause()
        await pilot.pause()
        assert table.cursor_row == 0

        # a lone g followed by a timeout must not move the cursor
        await pilot.press("G")
        await pilot.pause()
        bottom_row = table.row_count - 1
        await pilot.press("g")
        await pilot.pause(1.2)  # longer than _GG_TIMEOUT
        assert table.cursor_row == bottom_row
        await pilot.press("g")
        await pilot.pause()
        await pilot.pause()
        assert table.cursor_row == bottom_row


async def test_logs_level_column_coloring():
    """ERROR/INFO/WARNING cells carry rich styles; unknown levels stay plain."""
    from rich.text import Text

    from lazy_kafka.widgets._logs import LogEntry

    app = LazyKafka()
    handler = app.log_handler
    handler.entries.append(LogEntry("ERROR", "x", "boom"))
    handler.entries.append(LogEntry("INFO", "x", "ok"))
    handler.entries.append(LogEntry("WARNING", "x", "hmm"))
    handler.entries.append(LogEntry("NOTICE", "x", "unknown level"))

    async with app.run_test(size=(120, 30)) as pilot:
        await pilot.press("L")
        await pilot.pause()
        table = app.screen.query_one("#logs-table")

        for row, (level, expected_style) in enumerate(
            [("ERROR", "red"), ("INFO", "green"), ("WARNING", "yellow")]
        ):
            cell = table.get_cell_at(type(table.cursor_coordinate)(row, 1))
            assert cell.plain == level
            assert cell.style == expected_style, (level, cell.style)
        unknown_cell = table.get_cell_at(type(table.cursor_coordinate)(3, 1))
        assert unknown_cell == "NOTICE"  # plain string, unstyled
        assert not isinstance(unknown_cell, Text)


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



async def test_message_sparkline_shows_timestamp_distribution():
    """The Messages screen sparkline reflects the loaded messages' timestamps."""
    from unittest.mock import MagicMock

    from textual.widgets import Sparkline

    from lazy_kafka.topic import LazyKafkaMessage
    from lazy_kafka.widgets.topic_details import TopicDetails, TopicDetailsWidget

    messages = [
        LazyKafkaMessage(
            "2024-01-01T00:00:%02d+00:00" % s, s, b"key", "body"
        )
        for s in range(4)
    ]
    messages += [LazyKafkaMessage("2024-01-01T00:01:00+00:00", 4, b"key", "late")]

    app = LazyKafka()
    async with app.run_test(size=(120, 40)) as pilot:
        hook = MagicMock()
        hook.config = app.lazy_kafka_config.kafka
        await app.push_screen(TopicDetails(hook=hook, topic="test-topic"))
        await pilot.pause()

        details_widget = app.screen.query_one(TopicDetailsWidget)
        details_widget._update_sparkline(messages)
        await pilot.pause()

        sparkline = app.screen.query_one("#message-distribution", Sparkline)
        data = sparkline.data
        assert data is not None and len(data) == 100
        assert sum(data) == 5
        # bucket i covers seconds [i * 0.6, (i + 1) * 0.6) of the message range
        # (0s..3s, plus the late message at 60s -> clamped into the last bucket)
        expected = [0] * 100
        for second in (0, 1, 2, 3):
            expected[int(second / 60 * 100)] += 1
        expected[99] += 1
        assert data == expected
