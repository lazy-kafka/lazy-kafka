"""Main CLI app to manage common config."""
import typer
from typing_extensions import Annotated

from . import _kafka
from . import _version

__all__ = ["app"]

app = typer.Typer(rich_markup_mode="rich", callback=_version.callback)

app.add_typer(_kafka.app, name="kafka")

@app.callback()
def config_file(
    config_file: Annotated[
        bool,
        typer.Option(
            "--config-file",
            help="Path to lazy-kafka config file.",
            rich_help_panel="[i][green]Customization and Utils[/]"
        ),
] = False,
):
    """Overwrite the default app config."""
    print(f"hello {config_file}")

