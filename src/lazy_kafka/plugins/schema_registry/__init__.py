"""Schema Registry plugin — browse and manage subjects/schemas."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from lazy_kafka.plugin import register
from lazy_kafka.registry import SchemaRegistry
from lazy_kafka.widgets.registry import SchemaRegistryPanel

if TYPE_CHECKING:
    import typer
    from textual.widget import Widget

    from lazy_kafka.config import Configuration

_LOGGER = logging.getLogger(__name__)


class SchemaRegistryPlugin:
    name = "schema-registry"
    tab_label = "Schema Registry"
    tab_id = "tab-schema"
    cli_name = "schema-registry"

    def build_panel(self, config: Configuration) -> Widget | str:
        try:
            hook = SchemaRegistry(config.registry)
        except (ConnectionRefusedError, AssertionError) as exc:
            _LOGGER.error("schema-registry: cannot connect", exc_info=exc)
            return "No connection"
        return SchemaRegistryPanel(id=self.tab_id, classes="has-border", hook=hook)

    def build_cli(self) -> typer.Typer | None:
        from lazy_kafka.plugins.schema_registry.cli import app

        return app


register(SchemaRegistryPlugin())
