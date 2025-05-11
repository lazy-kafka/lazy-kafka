from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Generator

from textual.reactive import Reactive, reactive
from textual.widgets import (
    DataTable,
)

from lazy_kafka.topic import (
    KafkaClient,
    Topic,
    TopicData,
    TopicMetadata,
)
from lazy_kafka.widgets._status import Status
from lazy_kafka.widgets.common import (
    WidgetWithDataTable,
)
from lazy_kafka.widgets.topic_details import TopicDetails

if TYPE_CHECKING:
    from textual.widget import Widget

_LOGGER = logging.getLogger(__name__)


class TopicPanel(WidgetWithDataTable[Topic, TopicMetadata]):
    """Topics widget."""

    BORDER_TITLE = "Topics"
    BORDER_SUBTITLE = "status"
    BINDINGS = [
        ("enter", "details", "Details"),
    ]

    selected_id: Reactive[str] = reactive(str)
    details: Reactive[TopicData | None] = reactive(None)

    def action_details(self):
        _LOGGER.info("show details:")
        assert self.details is not None
        self.app.push_screen(TopicDetails(topic=self.details.topic))

    def __init__(self, hook: KafkaClient, *args, **kwargs):
        self.subjects = dict()
        self.hook = hook
        self.data_auto_refresh = False
        super().__init__(*args, **kwargs)
        _LOGGER.debug(self.subjects)

    def compose(self) -> Generator[Widget]:
        yield Status()
        yield DataTable(cursor_type="row", zebra_stripes=True)

    def on_mount(self):
        data_table = self.query_one(DataTable)
        data_table.add_column("Name")
        super().on_mount()

    def subject_to_table(self, response:dict[Topic, TopicMetadata], *args, **kwargs):
        return {i:i for i in response.keys()}
