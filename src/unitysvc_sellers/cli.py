"""Console script for ``unitysvc_sellers`` — the ``usvc_seller`` CLI."""

from __future__ import annotations

import importlib.metadata

import typer

from . import data
from .commands import groups as groups_cmd
from .commands import promotions as promotions_cmd
from .commands import services as services_cmd

# Importing tests.py registers list-tests/show-test/run-tests/skip-test/unskip-test
# as additional commands on services_cmd.app at import time.
from .commands import tests as _tests_cmd  # noqa: F401


def version_callback(value: bool) -> None:
    if value:
        version = importlib.metadata.version("unitysvc-sellers")
        typer.echo(f"unitysvc-sellers {version}")
        raise typer.Exit()


app = typer.Typer(
    help=(
        "UnitySVC seller CLI — local catalog tools and remote API operations.\n\n"
        "Local commands live under `usvc_seller data ...`. Remote commands "
        "(against the seller backend, via the unitysvc-sellers HTTP SDK) live "
        "under `usvc_seller services|promotions|groups`."
    ),
)


@app.callback()
def main(
    version: bool | None = typer.Option(
        None,
        "--version",
        "-V",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """UnitySVC seller CLI."""


# Local catalog tools
app.add_typer(data.app, name="data")

# Remote API command groups (use AsyncClient under the hood)
app.add_typer(services_cmd.app, name="services")
app.add_typer(promotions_cmd.app, name="promotions")
app.add_typer(groups_cmd.app, name="groups")


if __name__ == "__main__":
    app()
