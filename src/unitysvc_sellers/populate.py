"""Populate command - populate services by executing provider scripts."""

import os
import shutil
import subprocess
from pathlib import Path

import json5
import typer
from rich.console import Console

from .format_data import format_data_files
from .utils import find_files_by_schema

app = typer.Typer(help="Populate services")
console = Console()


def _install_requirements(requirements: list[str]) -> tuple[bool, str]:
    """Install requirements using uv pip or pip.

    Tries uv pip first (for uv-managed environments), then falls back to pip.

    Args:
        requirements: List of package names to install

    Returns:
        Tuple of (success, error_message)
    """
    # Try uv pip first if uv is available
    if shutil.which("uv"):
        result = subprocess.run(
            ["uv", "pip", "install", "--quiet"] + requirements,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return True, ""
        # If uv pip fails, try regular pip as fallback

    # Try regular pip
    if shutil.which("pip"):
        result = subprocess.run(
            ["pip", "install", "--quiet"] + requirements,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return True, ""
        return False, result.stderr

    return False, "Neither 'uv pip' nor 'pip' is available"


def _populator_sources(data_dir: Path, provider_filter: str | None) -> list[tuple[dict, Path, str]]:
    """Return ``[(services_populator, cwd, label)]`` for the repo's populator(s).

    Prefers a dedicated populator config — ``templates/config.json`` then a
    top-level ``config.json`` — holding ``{"services_populator": {...}}``, run
    from the repo root (so ``command: ["scripts/update_specs.py"]`` resolves
    naturally). This keeps ``provider.json`` a pure provider definition that the
    populator copies into each service folder verbatim.

    Falls back to legacy provider files carrying ``services_populator`` (run
    from the provider file's directory).
    """
    for rel in ("templates/config.json", "config.json"):
        cfg = data_dir / rel
        if not cfg.is_file():
            continue
        try:
            with open(cfg) as f:
                data = json5.load(f)
        except Exception:
            continue
        sp = data.get("services_populator") if isinstance(data, dict) else None
        if sp:
            return [(sp, data_dir, rel)]

    # Legacy: provider files (provider.json/toml) carrying services_populator.
    sources: list[tuple[dict, Path, str]] = []
    for provider_file, _fmt, pdata in find_files_by_schema(data_dir, "provider_v1"):
        name = pdata.get("name", "unknown")
        if provider_filter and name != provider_filter:
            continue
        sp = pdata.get("services_populator")
        if sp:
            sources.append((sp, provider_file.parent, name))
    return sources


@app.command()
def populate(
    data_dir: Path | None = typer.Argument(
        None,
        help="Directory containing provider data files (default: current directory)",
    ),
    provider_name: str | None = typer.Option(
        None,
        "--provider",
        "-p",
        help="Only populate services for a specific provider",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be executed without actually running commands",
    ),
):
    """
    Populate services by executing the repo's populator script.

    Reads the ``services_populator`` config from ``templates/config.json`` (or a
    top-level ``config.json``) and runs its command from the repo root, so a
    command like ``["scripts/update_specs.py"]`` resolves naturally. Legacy
    provider files carrying ``services_populator`` are still supported as a
    fallback.

    After successful execution, automatically runs formatting on all generated
    files (equivalent to ``usvc_seller specs format``).
    """
    # Set data directory
    if data_dir is None:
        data_dir = Path.cwd()

    if not data_dir.is_absolute():
        data_dir = Path.cwd() / data_dir

    if not data_dir.exists():
        console.print(f"[red]✗[/red] Data directory not found: {data_dir}", style="bold red")
        raise typer.Exit(code=1)

    console.print(f"[blue]Looking for populator config in:[/blue] {data_dir}\n")

    sources = _populator_sources(data_dir, provider_name)
    if not sources:
        console.print(
            "[yellow]No populator config found "
            "(templates/config.json, config.json, or a provider file with services_populator).[/yellow]"
        )
        raise typer.Exit(code=0)

    total_executed = 0
    total_skipped = 0
    total_failed = 0

    for services_populator, cwd, label in sources:
        try:
            command = services_populator.get("command")
            if not command:
                console.print(f"[yellow]⏭️  Skipping {label}: no command in services_populator[/yellow]")
                total_skipped += 1
                continue

            console.print(f"[bold cyan]Populating from:[/bold cyan] {label}")

            # Install requirements if specified
            requirements = services_populator.get("requirements", [])
            if requirements:
                if dry_run:
                    console.print(f"[yellow]  [DRY-RUN] Would install: {', '.join(requirements)}[/yellow]")
                else:
                    console.print(f"[dim]  Installing requirements: {', '.join(requirements)}[/dim]")
                    success, error_msg = _install_requirements(requirements)
                    if not success:
                        console.print(
                            f"[red]✗[/red] Failed to install requirements for {label}: {error_msg}",
                            style="bold red",
                        )
                        total_failed += 1
                        continue

            # Prepare environment variables from services_populator.envs
            env = os.environ.copy()
            populator_envs = services_populator.get("envs", {})
            if populator_envs:
                for key, value in populator_envs.items():
                    env[key] = str(value)
                console.print(f"[dim]  Set {len(populator_envs)} env var(s) from services_populator.envs[/dim]")

            # Build command - handle both string and list formats
            cmd_parts = command.split() if isinstance(command, str) else list(command)

            # Resolve script path relative to the working directory (repo root)
            script_path = cwd / cmd_parts[0]
            if script_path.exists():
                cmd_parts[0] = str(script_path)

            full_command = ["python3"] + cmd_parts

            if dry_run:
                console.print("[yellow]  [DRY-RUN] Would execute command[/yellow]")
                console.print(f"[yellow]    {' '.join(full_command)}[/yellow]")
                console.print(f"[yellow]  under  {cwd}[/yellow]")
                if populator_envs:
                    console.print("[yellow]  with environment variables:[/yellow]")
                    for key, value in populator_envs.items():
                        display_value = value if len(str(value)) < 8 else str(value)[:4] + "..."
                        console.print(f"[yellow]    {key}={display_value}[/yellow]")
                console.print()
                total_skipped += 1
                continue

            console.print(f"[blue]  Command:[/blue] {' '.join(full_command)}")
            console.print(f"[blue]  Working directory:[/blue] {cwd}")

            try:
                result = subprocess.run(full_command, cwd=cwd, env=env, capture_output=False, text=True)
                if result.returncode == 0:
                    console.print(f"[green]✓[/green] Successfully populated from {label}\n")
                    total_executed += 1
                else:
                    console.print(
                        f"[red]✗[/red] Command failed for {label} (exit code: {result.returncode})\n",
                        style="bold red",
                    )
                    total_failed += 1
            except subprocess.SubprocessError as e:
                console.print(f"[red]✗[/red] Failed to execute command for {label}: {e}\n", style="bold red")
                total_failed += 1

        except Exception as e:
            console.print(f"[red]✗[/red] Error processing {label}: {e}\n", style="bold red")
            total_failed += 1

    # Print summary
    console.print("\n" + "=" * 50)
    console.print("[bold]Populate Services Summary:[/bold]")
    console.print(f"  Populators run: {len(sources)}")
    console.print(f"  [green]✓ Successfully executed: {total_executed}[/green]")
    console.print(f"  [yellow]⏭️  Skipped: {total_skipped}[/yellow]")
    console.print(f"  [red]✗ Failed: {total_failed}[/red]")

    # Format generated files if any populate scripts executed successfully
    if total_executed > 0 and not dry_run:
        console.print("\n" + "=" * 50)
        console.print("[bold cyan]Formatting generated files...[/bold cyan]")
        console.print("[dim]Running automatic formatting to ensure data conforms to format specification[/dim]\n")

        try:
            # Format in-place (``check_only=False``).  Calling the
            # plain helper rather than the Typer-decorated ``format_data``
            # command — calling that as a function leaks
            # ``typer.Option(False)`` defaults through as ``OptionInfo``
            # objects, which evaluate truthy and silently turn the post-
            # populate format pass into a check-only run that never
            # rewrites the generated files.
            format_data_files(data_dir, check_only=False)
            console.print("\n[green]✓ Formatting completed successfully[/green]")
        except Exception as e:
            console.print(f"\n[yellow]⚠ Warning: Formatting failed: {e}[/yellow]")
            console.print("[dim]You may want to run 'usvc format' manually to fix formatting issues[/dim]")

    if total_failed > 0:
        raise typer.Exit(code=1)
