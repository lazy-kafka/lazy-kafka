from __future__ import annotations

import json
import logging
from typing import Any

from textual import events, work
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Container, Grid, Vertical
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import Reactive, reactive
from textual.validation import ValidationResult, Validator
from textual.widgets import (
    Button,
    DataTable,
    Input,
    Label,
    Pretty,
    TextArea,
)
from textual.widgets.data_table import DuplicateKey, RowDoesNotExist

from lazy_kafka import registry
from lazy_kafka.widgets._status import Status
from lazy_kafka.widgets.common import MyContainer, MyScrollableContainer
from lazy_kafka.utils import get_current_time

logging.basicConfig(level=logging.INFO)

_LOGGER = logging.getLogger(__name__)



class ValidSchemaType(Validator):
    """A custom validator."""

    def validate(self, value: str) -> ValidationResult:
        """Check a string is equal to its reverse."""
        if self.is_valid_schema_type(value):
            return self.success()
        else:
            return self.failure("That's not a palindrome :/")

    @staticmethod
    def is_valid_schema_type(value: str) -> bool:
        return value in registry.SchemaTypes


class CreateDialog(Container, can_focus=True):
    """Modal to display on creating new schema."""

    BORDER_TITLE = "Create new schema"
    BORDER_SUBTITLE = "edit"

    _tt = """{
      "$schema": "http://json-schema.org/draft-07/schema#",
      "title": "User",
      "description": "A Confluent Kafka Python User",
      "type": "object",
      "properties": {
        "name": {
          "description": "User's name",
          "type": "string"
        },
        "favorite_number": {
          "description": "User's favorite number",
          "type": "number",
          "exclusiveMinimum": 0
        },
        "favorite_color": {
          "description": "User's favorite color",
          "type": "string"
        }
      },
      "required": [ "name", "favorite_number", "favorite_color" ]
    }"""

    class Create(Message):
        """Color selected message."""

        def __init__(
            self, subject_name: str, schema_type: registry.SchemaTypes, schema: str
        ) -> None:
            self.subject_name = subject_name
            self.schema_type = schema_type
            self.schema = schema
            super().__init__()

    def compose(self) -> ComposeResult:
        text_area = TextArea(show_line_numbers=True, id="editor").code_editor(
            CreateDialog._tt
        )
        text_area.cursor_blink = False
        text_area.indent_width = 2
        # Register the json and highlight query
        # text_area.register_language(java_language, java_highlight_query)
        # Switch to Java
        text_area.language = "json"
        yield Grid(
            Input(placeholder="Subject name", id="subject-name"),
            Input(
                placeholder="JSON | AVRO | PROTOBUF",
                id="schema-type",
                validators=[ValidSchemaType()],
            ),
            text_area,
            Button("Create", variant="success", id="create"),
            Button("Cancel", variant="primary", id="cancel"),
            id="dialog",
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create":
            subject_name = self.query_one("#subject-name").value
            schema_type = self.query_one("#schema-type").value
            schema = self.query_one(TextArea).text
            # TODO: add json validator in the future?
            # NOTE: first the schema is parsed to get rid of oddities
            try:
                schema = json.dumps(json.loads(schema))
            except json.JSONDecodeError as e:
                _LOGGER.error(e.msg, exc_info=e)
                # TODO: dispatch invalid schema action
                return

            _LOGGER.debug(f"{subject_name=} {schema_type=}")
            _LOGGER.debug(f"{schema=}")
            self.post_message(self.Create(subject_name, schema_type, schema))
            await self.remove()
        else:
            await self.remove()


class DeleteDialog(Container, can_focus=True):
    """Modal to display on creating new schema."""

    BINDINGS = [
        ("y", "yes", "yes"),
        ("n", "no", "no"),
    ]

    class Delete(Message):
        """Color selected message."""

        def __init__(self, selected_id: str) -> None:
            self.selected_id = selected_id
            super().__init__()

    def __init__(self, selected_id: registry.Subject, *args, **kwargs):
        self.selected_id = selected_id
        super(Container, self).__init__(*args, **kwargs)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "delete":
            self.post_message(self.Delete(self.selected_id))
        await self.remove()

    async def on_key(self, event: events.Key) -> None:
        """Handle D as button press."""
        if event.key == "y":
            self.post_message(self.Delete(self.selected_id))
            await self.remove()
        elif event.key == "n":
            await self.remove()

        event.stop()

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(f":warning: Delete [italic]{self.selected_id}[/]?", id="question"),
            Button("Yes (y)", variant="error", id="delete"),
            Button("No (n)", variant="primary", id="cancel"),
            id="dialog",
        )


class SchemaRegistryPanel(MyContainer):
    """Schema Registry widget."""

    BORDER_TITLE = "Subjects"
    BORDER_SUBTITLE = "status"
    BINDINGS = [
        ("j", "next_widget_item", "↓"),
        ("k", "previous_widget_item", "↑"),
        ("f", "toggle_refresh", "Toggle follow"),
        ("c", "create", "create"),
        ("d", "delete", "delete"),
        ("escape", "unset_topic", "close"),
        Binding("slash", "search_subject", "Search", False),
    ]

    selected_id: Reactive[str] = reactive(str)
    details = reactive(registry.SubjectDetails)

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

    async def action_delete(self):
        """Action to display the delete dialog."""
        try:
            await self.query_one("#details").remove()
        except NoMatches:
            pass

        self.mount(DeleteDialog(self.selected_id, id="delete-dialog"))
        self.post_message(self.DialogOpen("#delete"))

    @work(exclusive=True, exit_on_error=False)
    async def on_delete_dialog_delete(self, message: DeleteDialog.Delete):
        r = await self.hook.asubjects_delete(
            message.selected_id, version=self.details["version"]
        )
        _LOGGER.info("Topic deleted %s", r)

    @work(exclusive=True)
    async def on_create_dialog_create(self, message: CreateDialog.Create):
        r = await self.hook.asubjects_create(
            message.subject_name,
            data={"schema": message.schema, "schemaType": message.schema_type},
        )
        if r.is_success:
            _LOGGER.info("Topic created %s", r)
        else:
            _LOGGER.error("%s", r.content.decode("utf8"))

    async def action_create(self):
        """Action to display the quit dialog."""
        try:
            await self.query_one("#details").remove()
        except NoMatches:
            pass
        self.mount(CreateDialog(id="create-dialog"))
        self.post_message(self.DialogOpen("TextArea"))

    async def action_load_data(self):
        for data_table in self.query(DataTable):
            self.load_data(data_table, display_load=False)

    async def action_search_subject(self) -> None:
        try:
            res = self.query_one(Input)
            await res.remove()
        except NoMatches:
            res = await self.mount(
                Input(placeholder="Search..."), before=self.query_one(DataTable)
            )
            # self.set_focus(res)
            res = self.query_one(Input)
            self.app.set_focus(res)

    def __init__(self, hook: registry.SchemaRegistry, *args: Any, **kwargs: Any):
        _LOGGER.critical("INIT")
        self.subjects: dict[str, str] = {"": ""}
        self.hook = hook
        self.data_auto_refresh = False
        super().__init__(*args, **kwargs)
        _LOGGER.debug(self.subjects)

    class Selected(Message):
        """Color selected message."""

        def __init__(self, selected_id: str) -> None:
            self.selected_id = selected_id
            super().__init__()

    class DialogOpen(Message):
        """Color selected message."""

        def __init__(self, selected_id: str) -> None:
            self.selected_id = selected_id
            super().__init__()

    def compose(self) -> Any:
        yield Vertical(
            Status(),
            DataTable(cursor_type="row", zebra_stripes=True),
        )

    def on_mount(self):
        data_table = self.query_one(DataTable)
        data_table.add_column("Subjects")
        self.update_timer = self.set_interval(2, self.action_load_data, pause=True)

    @work(exclusive=True, exit_on_error=False)
    async def on_schema_registry_panel_selected(
        self, message: SchemaRegistryPanel.Selected
    ) -> None:
        """Set reactive attribute.

        Currently -> Message() -> Reactive() -> watch_topic()
        """
        _LOGGER.info("HELLOOO %s", message)
        _LOGGER.debug(f"{message.selected_id=}")
        # Note, this should be in the init method ...
        self.selected_id = message.selected_id
        self.details = await self.hook.asubject_latest(message.selected_id)
        _LOGGER.debug(self.details)

    def on_data_table_focused(self, event):
        _LOGGER.debug("DATA TABLE FOC %s", f"{event!r}")

    async def on_focus(self, event):
        """Perform a single refresh on focus."""
        for data_table in self.query(DataTable):
            self.load_data(data_table)

    def watch_details(self, details: str):
        """Callback on topic changed.

        Args:
            topic:
        """
        try:
            details_panel = self.query_one(Pretty)
        except NoMatches as _:
            details_panel = MyScrollableContainer(
                Pretty([]), id="details", classes="box initial"
            )
            self.mount(details_panel)
            return
        self.query_one(Pretty).update(details)
        self.log(f"{details}")

    @work(exclusive=True)
    async def load_data(self, data_table: DataTable, display_load=True) -> None:
        """Load data.

        Args:
            display_load (bool): set to false to disable loading animation.
            data_table: DataTable instance to be updated.
        """
        data_table.loading = display_load
        self.subjects = {i: i for i in await self.hook.asubjects()}
        # For now, clearing the whole table looks viable...
        # problem is that it resets the highlighted row - annoying
        for i in self.subjects.values():
            try:
                data_table.add_row(i, key=i)
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

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        # The post_message method sends an event to be handled in the DOM
        _LOGGER.debug(f"selected: {event}")
        if event.row_key.value is None:
            _LOGGER.error("False event")
            return
        self.post_message(self.Selected(self.subjects[event.row_key.value]))

    def on_my_scrollable_container_completed(self):
        """This is quite ugly.

        I don't have anything quick to fix it up. It's not truly reactive
        as I need to wait for the animation to finish first. Then pull the values
        from the state and send attributes down.

        In that sense, it's reactive, but not 'data' reactive.

        Should be handled inside the details widget at least...
        """
        selected_id = self.selected_id
        if selected_id is None:
            raise ValueError
        self.query_one(Pretty).update(self.details)

    def on_input_changed(self, event: Input.Changed) -> None:
        logging.debug(event)
        TOKEN = event.value
        table = self.query_one(DataTable)
        table.loading = True
        table.clear()
        _rows = {
            k: v.replace(TOKEN, f"[dark_orange]{TOKEN}[/dark_orange]")
            for k, v in self.subjects.items()
            if TOKEN in v.lower()
        }
        for k, v in _rows.items():
            table.add_row(v, key=k)
#        for k, v in self.subjects.items():
#            if token in v.lower():
#                v.replace(token, f"[dark_orange]{token}[/dark_orange]")
#                table.add_row(v, key=k)

        table.loading = False
