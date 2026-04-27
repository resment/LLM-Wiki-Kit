"""Command-line interface for llm-wiki-kit."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from llm_wiki_kit import __version__
from llm_wiki_kit.init_kb import InitError, init_knowledge_base

app = typer.Typer(
    name="llm-wiki",
    help="Deterministic helpers for LLM-compiled Markdown knowledge bases.",
    no_args_is_help=True,
)
console = Console()


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"llm-wiki-kit {__version__}")
        raise typer.Exit


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        callback=_version_callback,
        help="Show the llm-wiki-kit version.",
    ),
) -> None:
    """Run llm-wiki commands."""


@app.command()
def init(
    target: Annotated[
        Path,
        typer.Argument(help="Directory where the knowledge base will be created."),
    ],
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Preview changes without writing files."),
    ] = False,
    force: Annotated[
        bool,
        typer.Option("--force", help="Allow writing into a non-empty directory."),
    ] = False,
) -> None:
    """Create a standard LLM Wiki knowledge base skeleton."""

    try:
        result = init_knowledge_base(target, dry_run=dry_run, force=force)
    except InitError as error:
        console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(code=1) from error

    action = "Would initialize" if dry_run else "Initialized"
    console.print(f"[green]{action}[/green] knowledge base at {result.root}")

    table = Table(title="Planned changes" if dry_run else "Created paths")
    table.add_column("Type")
    table.add_column("Path")

    for directory in result.plan.directories:
        table.add_row("dir", str(directory))
    for file_path in result.plan.files:
        table.add_row("file", str(file_path))

    console.print(table)
