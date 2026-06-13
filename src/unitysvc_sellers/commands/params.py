"""``usvc_seller params`` — create services from templates + parameters.

A *params* entry is just a template reference + parameter values (local, like a
spec) — inert until you **`instantiate`** it, at which point it produces a
backend service (an *instance of a template*). `instantiate` is the params-kind
analog of `specs upload`. Browse what you can instantiate with
`usvc_seller templates`; see the services it produced with `usvc_seller services`.

Capability pools opt in the same way: `instantiate` a pool-named template and
the resulting service joins ``/p/<pool>`` at the pool's uniform terms.
"""

from __future__ import annotations

import json
from typing import Any

import typer
from rich.console import Console

from ._helpers import (
    api_key_option,
    async_client,
    base_url_option,
    model_to_dict,
    run_async,
)
from .templates import _resolve_template

console = Console()

app = typer.Typer(
    help="Create services from templates + parameters (instantiate).",
)


def _coerce(value: str) -> Any:
    """Best-effort scalar coercion for ``-P key=value`` (JSON, else str)."""
    try:
        return json.loads(value)
    except (json.JSONDecodeError, ValueError):
        return value


def _parse_params(params: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for item in params:
        if "=" not in item:
            console.print(f"[red]Error:[/red] --param expects key=value, got '{item}'")
            raise typer.Exit(code=1)
        key, value = item.split("=", 1)
        out[key.strip()] = _coerce(value)
    return out


@app.command("instantiate")
def instantiate(
    template: str = typer.Argument(..., help="Template name or partial UUID."),
    param: list[str] = typer.Option(
        [],
        "--param",
        "-P",
        help="A template parameter as key=value (repeatable). Secret-typed params take the secret NAME, not the value.",
    ),
    name: str | None = typer.Option(
        None, "--name", help="Optional label for the service (defaults to template)."
    ),
    submit: bool = typer.Option(
        True,
        "--submit/--no-submit",
        help="Submit the rendered service for review (default), or leave it a draft.",
    ),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Instantiate a template + parameters into a service (the params-kind
    analog of ``specs upload``).

    Examples:
        usvc_seller params instantiate openai-compatible-llm \\
            -P api_base_url=https://ollama.example.com/v1 -P input_price=1.00
    """
    parameters = _parse_params(param)

    async def _impl():
        async with async_client(api_key, base_url) as client:
            stub = await _resolve_template(client, template)
            return model_to_dict(
                await client.instances.create(
                    stub["id"], parameters=parameters, name=name, submit=submit
                )
            )

    result = run_async(_impl(), error_prefix="Failed to instantiate template")
    verb = "Submitted for review" if submit else "Created as a draft"
    console.print(f"[green]✓[/green] {verb}")
    console.print(f"  instance_id: {result.get('instance_id')}")
    console.print(f"  task_id: {result.get('task_id')}")
    tail = (
        "submit it later with [cyan]usvc_seller services submit[/cyan]"
        if not submit
        else "track it in your staging list"
    )
    console.print(
        f"\n[dim]The service will appear under your staging list once ingest "
        f"completes — {tail}.[/dim]"
    )
