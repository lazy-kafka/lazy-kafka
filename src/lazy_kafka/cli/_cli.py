"""Main CLI app to manage common config."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Annotated

import typer
from rich import print
from rich.logging import RichHandler

from lazy_kafka import __version__
from lazy_kafka.config import Configuration
from lazy_kafka.plugin import iter_plugins, load_builtin_plugins

__all__ = ["app"]


def _set_up_logging(level="INFO"):
    FORMAT = "%(message)s"
    print(level)
    logging.basicConfig(
        level=level, format=FORMAT, datefmt="[%X]", handlers=[RichHandler(markup=True)]
    )


app = typer.Typer(rich_markup_mode="rich")

# Plugin CLIs are attached at import time: the shell imports this module
# whenever the user runs `lazy-kafka <subcommand>`, and each plugin contributes
# its own Typer sub-app.
load_builtin_plugins()
for _plugin in iter_plugins():
    if _plugin.cli_name is None:
        continue
    _sub_app = _plugin.build_cli()
    if _sub_app is None:
        continue
    app.add_typer(_sub_app, name=_plugin.cli_name)


def version_callback(value: bool) -> None:
    if value:
        print(f"LazyKafka CLI version: [green]{__version__}[/green]")
        raise typer.Exit()


@app.callback()
def global_options(
    config_file: Annotated[
        Path,
        typer.Option(
            "--config-file",
            "-f",
            help="Path to lazy-kafka config file.",
            rich_help_panel="[i][green]Customization and Utils[/]",
        ),
    ] = Configuration.default_config_file_path(),
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose", "-v", help="Logging verbosity.", rich_help_panel="Options"
        ),
    ] = False,
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            help="Show the version and exit.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
):
    """Overwrite the default app config."""
    # Configure app.
    if verbose:
        _set_up_logging(level="DEBUG")
    else:
        _set_up_logging()

    _LOGGER = logging.getLogger(__name__)
    _LOGGER.debug(f"LazyKafka {__version__} {config_file=} {verbose=}")
