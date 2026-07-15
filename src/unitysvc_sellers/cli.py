"""Console script for ``unitysvc_sellers`` — the ``usvc_seller`` CLI."""

from __future__ import annotations

import importlib.metadata

import typer

from . import specs as specs_group
from ._experimental import experimental_enabled
from .commands import files as files_cmd
from .commands import groups as groups_cmd
from .commands import params as params_cmd
from .commands import promotions as promotions_cmd
from .commands import secrets as secrets_cmd
from .commands import services as services_cmd
from .commands import templates as templates_cmd

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
        "Local commands live under `usvc_seller specs ...`. Remote commands "
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


# Local catalog tools (flat specs/ layout)
app.add_typer(specs_group.app, name="specs")

# Remote API command groups (use AsyncClient under the hood)
app.add_typer(services_cmd.app, name="services")
app.add_typer(promotions_cmd.app, name="promotions")
app.add_typer(groups_cmd.app, name="groups")
app.add_typer(secrets_cmd.app, name="secrets")
app.add_typer(files_cmd.app, name="files")
app.add_typer(templates_cmd.app, name="templates")
app.add_typer(params_cmd.app, name="params")

# Experimental command groups (unitysvc#1540) are registered only when the user
# opts in via UNITYSVC_EXPERIMENTAL, so `usvc_seller --help` hides them by
# default and they only work against a deployment that serves them (staging).
# Pattern for future experimental sub-apps (e.g. the order-based S3 delivery
# model):
#
#     from ._experimental import experimental_enabled
#     if experimental_enabled():
#         app.add_typer(orders_cmd.app, name="orders")
if experimental_enabled():
    pass  # no experimental commands yet — register them here when they land


if __name__ == "__main__":
    app()
