"""Logs widget for displaying application logs."""

from __future__ import annotations

import logging
from collections import deque
from datetime import datetime
from typing import TYPE_CHECKING, Deque

from textual import messages
from textual.binding import Binding
from textual.containers import Container
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Label

if TYPE_CHECKING:
    from textual.app import App

_LOGGER = logging.getLogger(__name__)

# Log level definitions - shared between LogHandler and LogsWidget
LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Module-level mapping from level name to index for O(1) lookup
LEVEL_TO_INDEX: dict[str, int] = {level: idx for idx, level in enumerate(LOG_LEVELS)}

# Minimum numeric level for each level name (for use in logging.Handler)
LOG_LEVEL_NUMERIC: dict[str, int] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# Log level to color mapping for styling
LOG_LEVEL_COLORS: dict[str, str] = {
    "DEBUG": "$text-disabled",
    "INFO": "$text",
    "WARNING": "$warning",
    "ERROR": "$error",
    "CRITICAL": "bold $error",
}


class LogEntry:
    """Represents a single log entry."""

    def __init__(
        self,
        level: str,
        logger_name: str,
        message: str,
        timestamp: datetime | None = None,
    ):
        self.level = level
        self.logger_name = logger_name
        self.message = message
        self.timestamp = timestamp or datetime.now()

    def to_tuple(self) -> tuple[str, str, str, str]:
        """Convert to tuple for display in DataTable."""
        time_str = self.timestamp.strftime("%H:%M:%S.%f")[:-3]
        return (time_str, self.level, self.logger_name, self.message)

    def get_color(self) -> str:
        """Get the CSS color for this log level."""
        return LOG_LEVEL_COLORS.get(self.level, "$text")

    def get_level_class(self) -> str:
        """Get the CSS class for a log level."""
        return f"level-{self.level.lower()}"


class LogHandler(logging.Handler):
    """Custom logging handler that stores log entries for display in the UI.
    
    This handler stores all log entries without filtering - filtering is done
    at the display level (LogsWidget) to avoid duplicate/inconsistent filtering.
    """

    def __init__(self, max_entries: int = 1000):
        super().__init__()
        # Ensure max_entries is at least 1
        self.max_entries: int = max(1, max_entries)
        self.entries: Deque[LogEntry] = deque(maxlen=self.max_entries)

    def emit(self, record: logging.LogRecord) -> None:
        """Handle a log record - store all entries without filtering."""
        # Use record.levelno directly instead of levelname to handle custom levels
        # Map numeric level to level name using standard logging levels
        level_name = logging.getLevelName(record.levelno)
        
        entry = LogEntry(
            level=level_name,
            logger_name=record.name,
            message=record.getMessage(),
            timestamp=datetime.fromtimestamp(record.created),
        )
        self.entries.append(entry)

    def get_entries(self) -> list[LogEntry]:
        """Get all log entries as a list."""
        return list(self.entries)

    def clear(self) -> None:
        """Clear all log entries."""
        self.entries.clear()

    def set_max_entries(self, max_entries: int) -> None:
        """Set the maximum number of entries to keep."""
        max_entries = max(1, max_entries)
        if max_entries == self.max_entries:
            return
        
        self.max_entries = max_entries
        # Recreate deque with new maxlen
        old_entries = list(self.entries)
        self.entries = deque(old_entries[-max_entries:], maxlen=max_entries)


class LogsWidget(Container, can_focus=True):
    """Widget for displaying logs with filtering and level control."""

    BINDINGS = [
        Binding("c", "clear_logs", "Clear logs"),
        Binding("up", "increase_level", "Increase log level"),
        Binding("down", "decrease_level", "Decrease log level"),
        Binding("b", "scroll_bottom", "Scroll to bottom"),
        Binding("t", "scroll_top", "Scroll to top"),
    ]

    DEFAULT_CSS = """
    LogsWidget {
        layout: vertical;
        height: 100%;
        width: 100%;
        
        &:focus {
            border: none;
        }
        
        Container {
            layout: horizontal;
            height: auto;
            width: 100%;
            padding: 0 1;
        }
        
        #logs-title {
            text-style: bold;
            color: $primary;
        }
        
        #level-label {
            padding-left: 2;
        }
        
        DataTable {
            width: 100%;
            height: 1fr;
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
            
            & > .datatable--cursor-row {
                background: $primary-lighten-3;
            }
            
            .level-debug {
                color: $text-disabled;
            }
            
            .level-info {
                color: $text;
            }
            
            .level-warning {
                color: $warning;
                text-style: bold;
            }
            
            .level-error {
                color: $error;
                text-style: bold;
            }
            
            .level-critical {
                color: $error;
                text-style: bold underline;
            }
        }
    }
    """

    # Use module-level LOG_LEVELS
    current_level_index: reactive[int] = reactive(1)  # Start at INFO (index 1)

    def __init__(self, log_handler: LogHandler | None = None, initial_level: str | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_handler = log_handler or LogHandler()
        self._data_table: DataTable | None = None
        self._initial_level = initial_level

    def on_mount(self) -> None:
        """Initialize the widget after mounting."""
        self._data_table = self.query_one("#logs-table", DataTable)
        self._setup_table()
        
        # Set initial level if provided
        if self._initial_level and self._initial_level in LEVEL_TO_INDEX:
            self.current_level_index = LEVEL_TO_INDEX[self._initial_level]
        
        self._update_level_display()
        self._update_table()
        # Start with focus on the table
        self.set_focus(self._data_table)
        # Set up periodic refresh to catch new log entries
        self.set_interval(0.1, self._check_for_updates)

    def watch_current_level_index(self, old: int, new: int) -> None:
        """React to log level changes."""
        # Only update display if widget is mounted and DOM is available
        if hasattr(self, '_data_table') and self._data_table:
            self._update_level_display()
        self._update_table()

    def _on_entries_updated(self) -> None:
        """Called when log_handler.entries is updated.
        
        This is triggered by a reactive watcher on the entries count.
        """
        self._update_table()

    def compose(self) -> Container.ComposeResult:
        with Container():
            yield Label("Logs", id="logs-title")
            yield Label("Level: DEBUG", id="level-label")
        
        yield DataTable(id="logs-table")
        yield Footer()

    def _check_for_updates(self) -> None:
        """Periodically check for new log entries and update the display."""
        self._update_table()

    def _update_entries_count(self) -> None:
        """Update the display when entries count changes."""
        # Just trigger a table update
        self._update_table()

    def _setup_table(self) -> None:
        """Set up the DataTable columns."""
        if self._data_table:
            self._data_table.clear()
            self._data_table.add_column("Time", width=12)
            self._data_table.add_column("Level", width=8)
            self._data_table.add_column("Logger", width=20)
            self._data_table.add_column("Message", width=100)

    def _update_level_display(self) -> None:
        """Update the log level display."""
        level_label = self.query_one("#level-label", Label)
        current_level = LOG_LEVELS[self.current_level_index]
        level_label.update(f"Level: [bold yellow]{current_level}[/]")

    def _passes_level_filter(self, entry: LogEntry) -> bool:
        """Check if a log entry passes the current level filter.
        
        Uses index-based comparison for consistency.
        """
        try:
            entry_level_index = LEVEL_TO_INDEX[entry.level]
            return entry_level_index >= self.current_level_index
        except KeyError:
            # Unknown level - include it to be safe
            return True

    def _update_table(self) -> None:
        """Update the table with current log entries.
        
        Filters entries based on current_level_index and displays them
        with appropriate styling.
        """
        if not self._data_table:
            return

        self._data_table.clear()
        # Don't call _setup_table() here - it's only needed on initial setup
        
        for entry in self.log_handler.get_entries():
            if self._passes_level_filter(entry):
                time_str, level, logger, message = entry.to_tuple()
                # Add row with the level as a styled cell
                self._data_table.add_row(
                    time_str,
                    f"[{entry.get_level_class()}]{level}[/]",
                    logger,
                    message,
                )
        
        # Scroll to bottom to show newest logs
        self._data_table.scroll_end()

    def action_clear_logs(self) -> None:
        """Clear all logs."""
        self.log_handler.clear()
        self._update_entries_count()
        if self._data_table:
            self._data_table.clear()
            self._setup_table()

    def action_increase_level(self) -> None:
        """Increase log level (show less verbose logs)."""
        if self.current_level_index < len(LOG_LEVELS) - 1:
            self.current_level_index += 1

    def action_decrease_level(self) -> None:
        """Decrease log level (show more verbose logs)."""
        if self.current_level_index > 0:
            self.current_level_index -= 1

    def action_scroll_bottom(self) -> None:
        """Scroll to the bottom of the logs."""
        if self._data_table:
            self._data_table.scroll_end()

    def action_scroll_top(self) -> None:
        """Scroll to the top of the logs."""
        if self._data_table:
            self._data_table.scroll_home()

    def update_from_handler(self) -> None:
        """Public method to update the table from the log handler's entries.
        
        Can be called externally to refresh the display.
        """
        self._update_table()




class LogsScreen(Screen):
    """Screen to display application logs."""

    # No BINDINGS here - the LogsWidget handles all key bindings
    # and the screen delegates to it via focus

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logs_widget: LogsWidget | None = None

    def compose(self) -> Screen.ComposeResult:
        # Get the log_handler and config from the app
        log_handler = getattr(self.app, 'log_handler', None)
        config = getattr(self.app, 'lazy_kafka_config', None)
        initial_level = getattr(config, 'log_level', "INFO") if config else "INFO"
        self._logs_widget = LogsWidget(log_handler=log_handler, initial_level=initial_level)
        yield self._logs_widget
        yield Footer()

    def on_mount(self) -> None:
        """Focus the logs widget on mount."""
        if self._logs_widget:
            self.set_focus(self._logs_widget)