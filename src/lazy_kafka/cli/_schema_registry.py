"""Schema Registry related CLI."""

from __future__ import annotations

import logging
import asyncio
from pathlib import Path
import json
from typing import Annotated

import rich.progress
import typer
from confluent_kafka import Consumer

from lazy_kafka import registry
from lazy_kafka.config import Configuration

_LOGGER = logging.getLogger(__name__)

CONSOLE = rich.console.Console(log_path=False)

app = typer.Typer()


@app.callback()
def schema_registry():
    """Interact with [b]Schema Registry[/]."""


# NOTE: the commands below repeat the config file path option, this is due
# to ctx object not playing nice and me not grasping fully:
# https://github.com/fastapi/typer/discussions/1195
@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def create(
    ctx: typer.Context,
    subject: Annotated[str, typer.Argument(help="subject name", show_default=False)],
    schema: Annotated[str, typer.Argument(help="schema string", show_default=False)],
    # TODO: somehow resuse registry.NewSubject to create args/options
    schema_type: Annotated[
        registry.SchemaTypes,
        typer.Argument(
            help="schema format",
            show_default=True,
        ),
    ] = registry.SchemaTypes.JSON,
    config_file: Annotated[
        Path,
        typer.Option(
            "--config-file",
            "-f",
            help="Path to lazy-kafka config file.",
            rich_help_panel="[i][green]Customization and Utils[/]",
        ),
    ] = Configuration.default_config_file_path(),
):
    """Submit a new schema  ([i]`subject`[/]).

    If the schema already exists, a "latest" version is going to be registered.
    """
    cfg = Configuration().from_toml(config_file)
    client = registry.SchemaRegistry(cfg.registry)
    version = typer.prompt(
        "Provide the schema version (int). Press enter to use 'latest'."
    )

    async def _subject_create():
        await client.asubjects_create(
            subject=registry.Subject(subject),
            data=registry.SubjectNew(schema=schema, schemaType=schema_type),
        )

    _loop = asyncio.get_event_loop()
    _loop.run_in_executor(None, _subject_create)
