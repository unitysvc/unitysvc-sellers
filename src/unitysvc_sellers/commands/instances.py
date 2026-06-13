"""``usvc_seller instances`` — create & manage services from platform templates.

A *template instance* is your record of ``template + parameters`` and the
service it renders to. ``create`` instantiates a template (one ``-P key=value``
per parameter); by default it also submits the service for review
(``--no-submit`` to leave it a draft). ``list`` / ``show`` / ``delete`` manage
your instances. Browse what you can instantiate with ``usvc_seller templates``.

Capability pools opt in the same way: ``create`` from a pool-named template and
the resulting service joins ``/p/<pool>`` at the pool's uniform terms.
"""

from __future__ import annotations

import json
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from ._helpers import (
    api_key_option,
    async_client,
    base_url_option,
    model_list,
    model_to_dict,
    run_async,
)
from .templates import _resolve_template

console = Console()

app = typer.Typer(
    help="Create and manage services from templates (create, list, show, delete).",
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


@app.command("create")
def create_instance(
    template: str = typer.Argument(..., help="Template name or partial UUID."),
    param: list[str] = typer.Option(
        [],
        "--param",
        "-P",
        help="A template parameter as key=value (repeatable). Secret-typed params take the secret NAME, not the value.",
    ),
    name: str | None = typer.Option(
        None, "--name", help="Optional label for the instance (defaults to template)."
    ),
    submit: bool = typer.Option(
        True,
        "--submit/--no-submit",
        help="Submit the rendered service for review (default), or leave it a draft.",
    ),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Create a service from a template + parameters.

    Examples:
        usvc_seller instances create openai-compatible-llm \\
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

    result = run_async(_impl(), error_prefix="Failed to create instance")
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


@app.command("list")
def list_instances(
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """List your template instances and their service status."""

    async def _impl():
        async with async_client(api_key, base_url) as client:
            return model_list(await client.instances.list(limit=500))

    instances = run_async(_impl(), error_prefix="Failed to list instances")

    if not instances:
        console.print("[dim]No instances yet — create one with[/dim] [cyan]usvc_seller instances create[/cyan]")
        return
    if output_format == "json":
        console.print(json.dumps(instances, indent=2, default=str))
        return

    table = Table(title="Template Instances")
    table.add_column("Name", style="bold")
    table.add_column("Template")
    table.add_column("Service")
    table.add_column("ID", style="dim")
    for inst in instances:
        tpl = inst.get("template_name") or ""
        ver = inst.get("template_version")
        table.add_row(
            inst.get("name", ""),
            f"{tpl} {ver}".strip(),
            str(inst.get("service_status") or "—"),
            str(inst.get("id", ""))[:8],
        )
    console.print(table)


@app.command("show")
def show_instance(
    instance_id: str = typer.Argument(..., help="Instance ID (full or partial UUID)."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Show one instance: parameters, template, and linked service status."""

    async def _impl():
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.instances.get(instance_id))

    inst = run_async(_impl(), error_prefix="Failed to show instance")
    console.print(json.dumps(inst, indent=2, default=str))


@app.command("delete")
def delete_instance(
    instance_id: str = typer.Argument(..., help="Instance ID (full or partial UUID)."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Delete an instance record (the linked service is not unpublished)."""

    async def _impl():
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.instances.delete(instance_id))

    run_async(_impl(), error_prefix="Failed to delete instance")
    console.print(f"[green]✓[/green] Instance {instance_id} deleted")
