"""Command-line interface for llm-wiki-kit."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from llm_wiki_kit import __version__
from llm_wiki_kit.export import export_current
from llm_wiki_kit.init_kb import InitError, init_knowledge_base
from llm_wiki_kit.linting import lint_exit_code, lint_json, lint_knowledge_base
from llm_wiki_kit.manifest import scan_manifest
from llm_wiki_kit.mini_kb import create_mini_kb
from llm_wiki_kit.prompts import render_ingest_prompt, render_lint_ai_prompt
from llm_wiki_kit.source_card import create_source_card

app = typer.Typer(
    name="llm-wiki",
    help="Deterministic helpers for LLM-compiled Markdown knowledge bases.",
    no_args_is_help=True,
)
manifest_app = typer.Typer(help="Manage raw source manifests.")
source_card_app = typer.Typer(help="Create source card templates.")
prompt_app = typer.Typer(help="Render prompts for external agents.")
export_app = typer.Typer(help="Export confirmed knowledge for AI tools.")
mini_kb_app = typer.Typer(help="Create mini knowledge-base drafts.")
console = Console()

app.add_typer(manifest_app, name="manifest")
app.add_typer(source_card_app, name="source-card")
app.add_typer(prompt_app, name="prompt")
app.add_typer(export_app, name="export")
app.add_typer(mini_kb_app, name="mini-kb")


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


@manifest_app.command("scan")
def manifest_scan(
    kb_root: Annotated[Path, typer.Argument(help="Knowledge base root.")],
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without writing.")] = False,
    output_format: Annotated[
        str,
        typer.Option("--format", help="Output format: markdown or json."),
    ] = "markdown",
) -> None:
    """Scan ai_kb/raw and update source_manifest.md."""

    if output_format not in {"markdown", "json"}:
        console.print("[red]Error:[/red] --format must be markdown or json")
        raise typer.Exit(code=2)
    content = scan_manifest(kb_root, output_format=output_format, dry_run=dry_run)
    if dry_run or output_format == "json":
        console.print(content)
    else:
        console.print("[green]Updated[/green] ai_kb/wiki/source_manifest.md")


@source_card_app.command("create")
def source_card_create(
    kb_root: Annotated[Path, typer.Argument(help="Knowledge base root.")],
    raw_source: Annotated[Path, typer.Argument(help="Raw source path under ai_kb/raw.")],
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without writing.")] = False,
    force: Annotated[
        bool,
        typer.Option("--force", help="Overwrite an existing source card."),
    ] = False,
) -> None:
    """Create a source card template for a raw source."""

    try:
        result = create_source_card(kb_root, raw_source, dry_run=dry_run, force=force)
    except (FileExistsError, FileNotFoundError, ValueError) as error:
        console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(code=1) from error
    action = "Would create" if dry_run else "Created"
    console.print(f"[green]{action}[/green] {result.path}")


@prompt_app.command("ingest")
def prompt_ingest(
    kb_root: Annotated[Path, typer.Argument(help="Knowledge base root.")],
    raw_source: Annotated[Path, typer.Argument(help="Raw source path under ai_kb/raw.")],
    output: Annotated[Path | None, typer.Option("--output", help="Write prompt to file.")] = None,
    copy: Annotated[
        bool,
        typer.Option("--copy", help="Reserved for clipboard support; prints prompt in Phase 2."),
    ] = False,
) -> None:
    """Render an ingest prompt for an external agent."""

    prompt = render_ingest_prompt(kb_root, raw_source)
    if output:
        output.write_text(prompt, encoding="utf-8")
        console.print(f"[green]Wrote[/green] {output}")
    else:
        console.print(prompt)
    if copy:
        console.print(
            "[yellow]Clipboard copy is not implemented in Phase 2; prompt was printed.[/yellow]"
        )


@prompt_app.command("lint-ai")
def prompt_lint_ai(
    kb_root: Annotated[Path, typer.Argument(help="Knowledge base root.")],
) -> None:
    """Render a semantic lint prompt for an external agent."""

    console.print(render_lint_ai_prompt(kb_root))


@app.command("lint")
def lint_command(
    kb_root: Annotated[Path, typer.Argument(help="Knowledge base root.")],
    json_output: Annotated[bool, typer.Option("--json", help="Print JSON output.")] = False,
    max_current_age: Annotated[
        int,
        typer.Option("--max-current-age", help="Warn when current pages are older than this."),
    ] = 30,
) -> None:
    """Run deterministic knowledge-base lint checks."""

    issues = lint_knowledge_base(kb_root, max_current_age=max_current_age)
    if json_output:
        console.print(lint_json(issues))
    else:
        table = Table(title="Lint Issues")
        table.add_column("Severity")
        table.add_column("Code")
        table.add_column("Path")
        table.add_column("Message")
        for issue in issues:
            table.add_row(issue.severity, issue.code, issue.path, issue.message)
        console.print(table)
    raise typer.Exit(code=lint_exit_code(issues))


@export_app.command("current")
def export_current_command(
    kb_root: Annotated[Path, typer.Argument(help="Knowledge base root.")],
    single_file: Annotated[
        str | None,
        typer.Option("--single-file", help="Also write a combined Markdown file."),
    ] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without writing.")] = False,
) -> None:
    """Export confirmed current pages to export_for_ai/current."""

    result = export_current(kb_root, single_file=single_file, dry_run=dry_run)
    action = "Would export" if dry_run else "Exported"
    console.print(f"[green]{action}[/green] {len(result.files)} files")
    for file_path in result.files:
        console.print(str(file_path))


@mini_kb_app.command("create")
def mini_kb_create(
    kb_root: Annotated[Path, typer.Argument(help="Knowledge base root.")],
    topic: Annotated[str, typer.Option("--topic", help="Mini-kb topic.")],
    purpose: Annotated[str, typer.Option("--purpose", help="Mini-kb purpose.")],
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without writing.")] = False,
    force: Annotated[bool, typer.Option("--force", help="Overwrite an existing mini-kb.")] = False,
) -> None:
    """Create a mini-kb draft."""

    try:
        result = create_mini_kb(kb_root, topic=topic, purpose=purpose, dry_run=dry_run, force=force)
    except FileExistsError as error:
        console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(code=1) from error
    action = "Would create" if dry_run else "Created"
    console.print(f"[green]{action}[/green] {result.path}")
