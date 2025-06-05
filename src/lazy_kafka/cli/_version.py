import logging
import typer
from typing_extensions import Annotated
from typing import Union

from lazy_kafka import __version__
from lazy_kafka._logging import setup_logging

app = typer.Typer()

def version_callback(value: bool) -> None:
    if value:
        print(f"LazyKafka CLI version: [green]{__version__}[/green]")
        raise typer.Exit()

@app.callback()
def callback(
    version: Annotated[
        Union[bool, None],
        typer.Option(
            "--version",
            help="Show the version and exit.",
            callback=version_callback
        ),
    ] = None,
    verbose: bool = typer.Option(False, help="Enable verbose output"),
) -> None:
    """
    LazyKafka CLI - Interact with message [i]streams[/i] from the terminal.

    Read more in the docs: [link=https://tmon.xyz/lazy-kafka-cli/]link=https://tmon.xyz/lazy-kafka-cli/[/link].
    """

    log_level = logging.DEBUG if verbose else logging.INFO

    setup_logging(level=log_level)
