from __future__ import annotations

import logging
from typing import Any

from textual.reactive import Reactive, reactive
from textual.widgets import (
    DataTable,
)

from lazy_kafka import connect
from lazy_kafka.widgets._status import Status
from lazy_kafka.widgets.common import (
    WidgetWithDataTable,
)

_LOGGER = logging.getLogger(__name__)


def _apply_styling(d: connect.ConnectorData) -> connect.ConnectorData:
    """

    Possible states:
        RUNNING
        FAILED
        RESTARTING.

    Args:
        d:

    Returns:

    """
    if d.state == "RUNNING":
        state = f"[italic green]{d.state}[/italic green]"
    elif d.state == "FAILED":
        state = f"[italic red]{d.state}[/italic red]"
    else:
        state = d.state

    _d2 = connect.ConnectorData(
        d.name,
        state,
        d.worker_id,
        d.type,
    )
    return _d2


def connector_to_data_table_row(data: connect.ConnectorData) -> tuple:
    return _apply_styling(data).to_tuple()


class KConnectPanel(WidgetWithDataTable[connect.ConnectorData, Any]):
    """KafkaConnect widget."""

    BORDER_TITLE = "Connectors"
    BORDER_SUBTITLE = "status"

    BINDINGS = [
        ("c", "create", "create"),
        ("d", "delete", "delete"),
    ]

    selected_id: Reactive[str] = reactive(str)
    details: Reactive[connect.ConnectorData] = reactive(connect.ConnectorData())


    def __init__(self, hook: connect.Connect, *args: Any, **kwargs: Any):
        self.subjects = dict()
        self.hook = hook
        self.data_auto_refresh = False
        super().__init__(*args, **kwargs)
        _LOGGER.debug(self.subjects)

    def compose(self) -> Any:
        yield Status()
        yield DataTable(cursor_type="row", zebra_stripes=True)

    def on_mount(self):
        """Initialize data table with columns."""
        data_table = self.query_one(DataTable)
        data_table.add_column("Name")
        data_table.add_column("State")
        data_table.add_column("Worker ID")
        data_table.add_column("Type")
        super().on_mount()

    def subject_to_table(self, response: dict[str, Any], *args, **kwargs):
        """Transform raw `hook.asubjects` results into DataTable dict values."""
        return connect.ConnectorData.from_response(response)
    
    def apply_filter(self, data: connect.ConnectorData, token: str, *, textual_styling = "dark_orange") -> connect.ConnectorData:
        """Apply textual highlighting on values."""
        _d = {
            k: v.replace(
                token,
                f"[{textual_styling}]{token}[/{textual_styling}]",
            )
            for k,v in data.to_dict().items()
        }
        return connect.ConnectorData(**_d)


