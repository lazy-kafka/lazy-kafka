"""Kafka Connect related CLI."""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Annotated

import typer

from lazy_kafka.config import Configuration
from lazy_kafka.connect import Connect, ConnectionRefusedError, ConnectorData

_LOGGER = logging.getLogger(__name__)

app = typer.Typer()


# NOTE: the status listing lives in the callback (with
# `invoke_without_command`) so that `lazy-kafka connectors` works bare,
# while leaving room for future sub-commands.
@app.callback(invoke_without_command=True)
def connectors(
    ctx: typer.Context,
    config_file: Annotated[
        Path | None,
        typer.Option(
            "--config-file",
            "-f",
            help="Path to lazy-kafka config file.",
            rich_help_panel="[i][green]Customization and Utils[/]",
        ),
    ] = None,
):
    """Print the status of all Kafka [b]connectors[/] as a JSON list.

    Each entry carries the same data as the connectors dashboard:
    name, state, worker_id and type.
    """
    if ctx.invoked_subcommand is not None:
        return
    if config_file is None:
        # Tolerate a missing user config; fall back to defaults.
        cfg = Configuration.from_local_config()
    else:
        cfg = Configuration.from_toml(config_file)
    try:
        client = Connect(cfg.connect)
    except (ConnectionRefusedError, AssertionError) as exc:
        _LOGGER.error("Cannot connect: %s", exc)
        raise typer.Exit(code=1) from exc

    # `alist` returns the raw `/connectors?expand=status` payload; parse it
    # the same way the connectors dashboard does.
    response = asyncio.run(client.alist())
    connector_data = ConnectorData.from_response(response)
    typer.echo(
        json.dumps([data.to_dict() for data in connector_data.values()], indent=2)
    )
