"""Console script for ``unitysvc_sellers`` — the ``usvc_seller`` CLI."""

from __future__ import annotations

import importlib.metadata

import typer

from . import data


def version_callback(value: bool) -> None:
    if value:
        version = importlib.metadata.version("unitysvc-sellers")
        typer.echo(f"unitysvc-sellers {version}")
        raise typer.Exit()


app = typer.Typer(help="UnitySVC seller CLI — local data organization tools.")


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


app.add_typer(data.app, name="data")


if __name__ == "__main__":
    app()
