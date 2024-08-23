from __future__ import annotations

import logging

from textual import work
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import Reactive, reactive
from textual.widgets import (
    DataTable,
    Pretty,
)

from lazy_kafka.topic import TopicData, list_topics, topic_data_to_dict
from lazy_kafka.widgets.common import Details, MyContainer, MyScrollableContainer

_LOGGER = logging.getLogger(__name__)


class TopicPanel(MyContainer):
    """Topics widget."""

    BORDER_TITLE = "Topics"
    BORDER_SUBTITLE = "status"
    BINDINGS = [
        ("j", "next_widget_item", "next"),
        ("k", "previous_widget_item", "prev"),
        ("escape", "unset_topic", "close"),
    ]

    topic: Reactive[TopicData] = reactive(TopicData())

    def action_next_widget_item(self):
        self.query_one(DataTable).action_cursor_down()

    def action_previous_widget_item(self):
        self.query_one(DataTable).action_cursor_up()

    def __init__(self, *args, **kwargs):
        self.TOPICS = dict()
        for k in list_topics():
            self.TOPICS[k.topic] = k
        super().__init__(*args, **kwargs)
        self.log(self.TOPICS)

    class Selected(Message):
        """Color selected message."""

        def __init__(self, topic: TopicData) -> None:
            self.topic = topic
            _LOGGER.debug(f"INIT: {self.topic!r}")
            super().__init__()

    def compose(self):
        yield DataTable()

    def on_mount(self):
        for data_table in self.query(DataTable):
            data_table.loading = True
            self.load_data(data_table)

    def on_topic_panel_selected(self, message: TopicPanel.Selected) -> None:
        """Set reactive attribute.

        Currently -> Message() -> Reactive() -> watch_topic()
        """
        self.topic = message.topic

    def watch_topic(self, topic: TopicData):
        """Callback on topic changed.

        Args:
            topic:
        """
        try:
            topic_details = self.query_one(Details)
        except NoMatches as _:
            details_panel = MyScrollableContainer(
                Details(), Pretty([]), id="details", classes="box initial"
            )
            self.mount(details_panel)
            return
        topic_details.detail_name = (
            "[b]topic: [/b]" + str(topic.topic) + str(topic.partitions)
        )
        self.query_one(Pretty).update(topic_data_to_dict(topic))
        self.log(f"{topic}")

    @work(exclusive=True, thread=True)
    async def load_data(self, data_table: DataTable) -> None:
        data_table.add_column("Name")
        j = list_topics()
        for t in j:
            data_table.add_row(t.topic)
        data_table.loading = False

    def on_data_table_cell_highlighted(self, event: DataTable.CellHighlighted) -> None:
        # The post_message method sends an event to be handled in the DOM
        self.log(f"selected: {self.TOPICS[event.value]}")
        self.post_message(self.Selected(self.TOPICS[event.value]))

    def on_my_scrollable_container_completed(self):
        """This is quite ugly.

        I don't have anything quick to fix it up. It's not truly reactive
        as I need to wait for the animation to finish first. Then pull the values
        from the state and send attributes down.

        In that sense, it's reactive, but not 'data' reactive.

        Should be handled inside the details widget at least...
        """
        topic = self.topic
        if topic.topic is None:
            raise ValueError
        topic_details = self.query_one(Details)
        topic_details.detail_name = (
            "[b]topic: [/b]" + str(topic.topic) + str(topic.partitions)
        )
        self.query_one(Pretty).update(topic_data_to_dict(topic))
