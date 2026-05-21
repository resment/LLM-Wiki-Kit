"""Command-line interface for Linta."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from linta import __version__
from linta.agent_access import (
    AGENTS,
    access_config_path,
    agent_access_json,
    agent_access_markdown,
    configure_agent_access,
    normalize_agent,
    read_agent_access_config,
    set_agent_access,
)
from linta.claude_desktop import (
    build_claude_project_instructions,
    claude_desktop_status_json,
    claude_project_instructions_json,
    inspect_claude_desktop_status,
    render_claude_desktop_config,
)
from linta.doctor import doctor_json, doctor_markdown, run_doctor
from linta.export import export_current
from linta.hermes import (
    configure_knowledge_base_profile,
    inspect_hermes_status,
    install_skills,
    render_bootstrap_prompt,
)
from linta.indexes import build_indexes
from linta.init_kb import InitError, init_knowledge_base
from linta.linting import lint_exit_code, lint_json, lint_knowledge_base
from linta.maintenance import maintenance_json, maintenance_markdown, run_daily_maintenance
from linta.manifest import scan_manifest
from linta.mcp_server import serve_mcp_stdio
from linta.migration import migration_json, migration_markdown, run_rename_migration
from linta.mini_kb import create_mini_kb
from linta.prompts import (
    render_entities_prompt,
    render_ingest_prompt,
    render_lint_ai_prompt,
    render_tag_prompt,
)
from linta.raw_import import RAW_SOURCE_TYPES, import_raw_source
from linta.source_card import create_source_card
from linta.tags import add_tags_to_file, list_tags, set_tags_in_file

app = typer.Typer(
    name="linta",
    help="Deterministic helpers for LLM-compiled Markdown knowledge bases.",
    no_args_is_help=True,
)
manifest_app = typer.Typer(help="Manage raw source manifests.")
source_card_app = typer.Typer(help="Create source card templates.")
prompt_app = typer.Typer(help="Render prompts for external agents.")
export_app = typer.Typer(help="Export confirmed knowledge for AI tools.")
mini_kb_app = typer.Typer(help="Create mini knowledge-base drafts.")
hermes_app = typer.Typer(help="Install optional Hermes adapter skills.")
agents_app = typer.Typer(help="Configure multi-agent read/write access.")
claude_desktop_app = typer.Typer(help="Configure Claude Desktop read-only MCP access.")
mcp_app = typer.Typer(help="Serve read-only MCP adapters.")
tags_app = typer.Typer(help="Manage Obsidian inline tags.")
index_app = typer.Typer(help="Build machine-readable indexes.")
raw_app = typer.Typer(help="Import uploaded raw source files.")
maintenance_app = typer.Typer(help="Run deterministic maintenance reports.")
console = Console()

app.add_typer(manifest_app, name="manifest")
app.add_typer(source_card_app, name="source-card")
app.add_typer(prompt_app, name="prompt")
app.add_typer(export_app, name="export")
app.add_typer(mini_kb_app, name="mini-kb")
app.add_typer(hermes_app, name="hermes")
app.add_typer(agents_app, name="agents")
app.add_typer(claude_desktop_app, name="claude-desktop")
app.add_typer(mcp_app, name="mcp")
app.add_typer(tags_app, name="tags")
app.add_typer(index_app, name="index")
app.add_typer(raw_app, name="raw")
app.add_typer(maintenance_app, name="maintenance")


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"Linta {__version__}")
        raise typer.Exit


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        callback=_version_callback,
        help="Show the Linta version.",
    ),
) -> None:
    """Run linta commands."""


def deprecated_main() -> None:
    """Run the deprecated llm-wiki command alias."""

    console.print("[yellow]Warning:[/yellow] `llm-wiki` is deprecated; use `linta` instead.")
    app()


def _write_agent_config(
    kb_root: Path,
    primary_agent: str,
    *,
    dry_run: bool,
    force: bool,
) -> None:
    try:
        result = configure_agent_access(
            kb_root,
            primary_agent=primary_agent,
            dry_run=dry_run,
            force=force,
        )
    except FileExistsError as error:
        console.print(f"[red]Error:[/red] {error}")
        console.print("Use --force to overwrite the existing agent access config.")
        raise typer.Exit(code=1) from error
    except ValueError as error:
        console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(code=2) from error
    action = "Would write" if dry_run else "Wrote"
    console.print(f"[green]{action}[/green] {result.path}")
    console.print(agent_access_markdown(result.config, result.path))


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
    """Create a standard Linta knowledge base skeleton."""

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


@app.command("doctor")
def doctor_command(
    kb_root: Annotated[Path, typer.Argument(help="Knowledge base root.")],
    json_output: Annotated[bool, typer.Option("--json", help="Print JSON output.")] = False,
) -> None:
    """Run read-only installation and knowledge-base diagnostics."""

    report = run_doctor(kb_root)
    if json_output:
        console.out(doctor_json(report))
    else:
        console.print(doctor_markdown(report))


@app.command("migrate")
def migrate_command(
    kb_root: Annotated[Path, typer.Argument(help="Knowledge base root.")],
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without writing.")] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Print JSON output.")] = False,
) -> None:
    """Migrate legacy llm-wiki rename-era files to Linta names."""

    report = run_rename_migration(kb_root, dry_run=dry_run)
    if json_output:
        console.out(migration_json(report))
    else:
        console.print(migration_markdown(report))


@manifest_app.command("scan")
def manifest_scan(
    kb_root: Annotated[Path, typer.Argument(help="Knowledge base root.")],
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without writing.")] = False,
    output_format: Annotated[
        str,
        typer.Option("--format", help="Output format: markdown or json."),
    ] = "markdown",
    preserve_manual_fields: Annotated[
        bool,
        typer.Option(
            "--preserve-manual-fields/--no-preserve-manual-fields",
            help="Preserve manually maintained manifest fields when possible.",
        ),
    ] = True,
) -> None:
    """Scan ai_kb/raw and update source_manifest.md."""

    if output_format not in {"markdown", "json"}:
        console.print("[red]Error:[/red] --format must be markdown or json")
        raise typer.Exit(code=2)
    content = scan_manifest(
        kb_root,
        output_format=output_format,
        dry_run=dry_run,
        preserve_manual_fields=preserve_manual_fields,
    )
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


@prompt_app.command("entities")
def prompt_entities(
    kb_root: Annotated[Path, typer.Argument(help="Knowledge base root.")],
    raw_source: Annotated[Path, typer.Argument(help="Raw source path under ai_kb/raw.")],
) -> None:
    """Render an entity-context update prompt for an external agent."""

    console.print(render_entities_prompt(kb_root, raw_source))


@prompt_app.command("tag")
def prompt_tag(
    kb_root: Annotated[Path, typer.Argument(help="Knowledge base root.")],
    markdown_path: Annotated[Path, typer.Argument(help="Markdown file to tag.")],
) -> None:
    """Render an Obsidian tag suggestion prompt for an external agent."""

    console.print(render_tag_prompt(kb_root, markdown_path))


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


@agents_app.command("wizard")
def agents_wizard(
    kb_root: Annotated[Path, typer.Argument(help="Knowledge base root.")],
    primary_agent: Annotated[
        str | None,
        typer.Option("--primary-agent", help="Primary read/write agent."),
    ] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without writing.")] = False,
    force: Annotated[bool, typer.Option("--force", help="Overwrite existing policy.")] = False,
) -> None:
    """Create a first-use multi-agent access policy."""

    selected = primary_agent or typer.prompt(
        f"Primary read/write agent ({', '.join(AGENTS)})",
        default="hermes",
    )
    _write_agent_config(kb_root, selected, dry_run=dry_run, force=force)


@agents_app.command("configure")
def agents_configure(
    kb_root: Annotated[Path, typer.Argument(help="Knowledge base root.")],
    primary_agent: Annotated[
        str,
        typer.Option("--primary-agent", help="Primary read/write agent."),
    ],
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without writing.")] = False,
    force: Annotated[bool, typer.Option("--force", help="Overwrite existing policy.")] = False,
) -> None:
    """Write a deterministic multi-agent access policy."""

    _write_agent_config(kb_root, primary_agent, dry_run=dry_run, force=force)


@agents_app.command("status")
def agents_status(
    kb_root: Annotated[Path, typer.Argument(help="Knowledge base root.")],
    json_output: Annotated[bool, typer.Option("--json", help="Print JSON output.")] = False,
) -> None:
    """Show the configured multi-agent access policy."""

    try:
        config = read_agent_access_config(kb_root)
    except (FileNotFoundError, ValueError) as error:
        console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(code=1) from error
    if json_output:
        console.out(agent_access_json(config))
    else:
        console.print(agent_access_markdown(config, access_config_path(kb_root)))


@agents_app.command("set")
def agents_set(
    kb_root: Annotated[Path, typer.Argument(help="Knowledge base root.")],
    agent: Annotated[str, typer.Option("--agent", help="Agent to update.")],
    mode: Annotated[str, typer.Option("--mode", help="read or write.")],
    read_scope: Annotated[
        str,
        typer.Option("--read-scope", help="exports-only, wiki-context, or full-kb."),
    ] = "wiki-context",
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without writing.")] = False,
) -> None:
    """Update one agent policy."""

    try:
        result = set_agent_access(
            kb_root,
            agent=agent,
            mode=mode,
            read_scope=read_scope,
            dry_run=dry_run,
        )
    except (FileNotFoundError, ValueError) as error:
        console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(code=2) from error
    action = "Would update" if dry_run else "Updated"
    console.print(f"[green]{action}[/green] {result.path}")
    console.print(agent_access_markdown(result.config, result.path))


@agents_app.command("policy")
def agents_policy(
    kb_root: Annotated[Path, typer.Argument(help="Knowledge base root.")],
    agent: Annotated[str, typer.Option("--agent", help="Agent to inspect.")],
    json_output: Annotated[bool, typer.Option("--json", help="Print JSON output.")] = False,
) -> None:
    """Show one agent policy."""

    try:
        config = read_agent_access_config(kb_root)
        normalized_agent = normalize_agent(agent)
    except (FileNotFoundError, ValueError) as error:
        console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(code=2) from error
    policy = config.agents[normalized_agent]
    payload = {
        "agent": normalized_agent,
        "mode": policy.mode,
        "read_scope": policy.read_scope,
        "primary": normalized_agent == config.primary_agent,
    }
    if json_output:
        import json

        console.out(json.dumps(payload, indent=2) + "\n")
    else:
        console.print(
            f"{normalized_agent}: mode={policy.mode}, read_scope={policy.read_scope}, "
            f"primary={payload['primary']}"
        )


@claude_desktop_app.command("config")
def claude_desktop_config(
    kb_root: Annotated[Path, typer.Argument(help="Knowledge base root.")],
) -> None:
    """Print a Claude Desktop MCP config snippet."""

    console.out(render_claude_desktop_config(kb_root))


@claude_desktop_app.command("status")
def claude_desktop_status(
    kb_root: Annotated[Path, typer.Argument(help="Knowledge base root.")],
    json_output: Annotated[bool, typer.Option("--json", help="Print JSON output.")] = False,
) -> None:
    """Show Claude Desktop policy and KB status."""

    try:
        status = inspect_claude_desktop_status(kb_root)
    except (FileNotFoundError, ValueError) as error:
        console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(code=1) from error
    if json_output:
        console.out(claude_desktop_status_json(status))
    else:
        console.print(f"KB root: {status.kb_root}")
        console.print(f"Claude Desktop mode: {status.policy_mode}")
        console.print(f"Read scope: {status.read_scope}")
        console.print(f"KB OK: {status.kb_ok}")
        console.print(
            "Project instructions: "
            f"linta claude-desktop project-instructions {status.kb_root}"
        )
        for warning in status.warnings:
            console.print(f"[yellow]Warning:[/yellow] {warning}")
        console.print(status.message)


@claude_desktop_app.command("project-instructions")
def claude_desktop_project_instructions(
    kb_root: Annotated[Path, typer.Argument(help="Knowledge base root.")],
    json_output: Annotated[bool, typer.Option("--json", help="Print JSON output.")] = False,
) -> None:
    """Print Claude Project instructions for practical Linta context."""

    instructions = build_claude_project_instructions(kb_root)
    if json_output:
        console.out(claude_project_instructions_json(instructions))
    else:
        console.out(instructions.instructions)


@mcp_app.command("serve")
def mcp_serve(
    kb_root: Annotated[Path, typer.Option("--kb-root", help="Knowledge base root.")],
    agent: Annotated[str, typer.Option("--agent", help="MCP agent name.")] = "claude-desktop",
) -> None:
    """Serve a read-only stdio MCP adapter."""

    serve_mcp_stdio(kb_root=kb_root, agent=agent)


@hermes_app.command("install-skills")
def hermes_install_skills(
    target: Annotated[
        Path | None,
        typer.Option("--target", help="Target skill directory."),
    ] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without copying.")] = False,
    force: Annotated[
        bool,
        typer.Option("--force", help="Overwrite existing skill directories."),
    ] = False,
) -> None:
    """Install bundled Hermes skills."""

    result = install_skills(target=target, dry_run=dry_run, force=force)
    action = "Would install" if dry_run else "Installed"
    console.print(f"[green]{action}[/green] Hermes skills to {result.target}")

    table = Table(title="Hermes Skills")
    table.add_column("Action")
    table.add_column("Skill")
    table.add_column("Path")
    for path in result.copied:
        table.add_row("copy", path.name, str(path))
    for path in result.skipped:
        table.add_row("skip", path.name, str(path))
    console.print(table)
    console.print(
        "Next: run [bold]linta hermes configure-kb <kb_root>[/bold] to bind a default KB."
    )


@hermes_app.command("configure-kb")
def hermes_configure_kb(
    kb_root: Annotated[Path, typer.Argument(help="Knowledge base root.")],
    target: Annotated[
        Path | None,
        typer.Option("--target", help="Hermes Linta skill directory."),
    ] = None,
    profile: Annotated[str, typer.Option("--profile", help="Profile name.")] = "default",
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without writing.")] = False,
    force: Annotated[bool, typer.Option("--force", help="Overwrite an existing profile.")] = False,
) -> None:
    """Bind a knowledge-base root for Hermes first-use workflows."""

    try:
        result = configure_knowledge_base_profile(
            kb_root,
            target=target,
            profile=profile,
            dry_run=dry_run,
            force=force,
        )
    except (FileExistsError, FileNotFoundError, ValueError) as error:
        console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(code=1) from error
    action = "Would write" if dry_run else "Wrote"
    console.print(f"[green]{action}[/green] Hermes profile {result.path}")
    if dry_run:
        console.print(result.content)


@hermes_app.command("bootstrap-prompt")
def hermes_bootstrap_prompt(
    kb_root: Annotated[Path, typer.Argument(help="Knowledge base root.")],
    target: Annotated[
        Path | None,
        typer.Option("--target", help="Hermes Linta skill directory."),
    ] = None,
    profile: Annotated[str, typer.Option("--profile", help="Profile name.")] = "default",
) -> None:
    """Print a natural-language Hermes Agent install prompt."""

    console.out(render_bootstrap_prompt(kb_root, target=target, profile=profile))


@hermes_app.command("status")
def hermes_status_command(
    target: Annotated[
        Path | None,
        typer.Option("--target", help="Hermes Linta skill directory."),
    ] = None,
) -> None:
    """Show installed Hermes skills and configured knowledge-base profiles."""

    status = inspect_hermes_status(target=target)
    console.print(f"Hermes target: {status.target}")
    console.print(f"Installed: {status.installed}")
    table = Table(title="Hermes Skills")
    table.add_column("Skill")
    table.add_column("Status")
    for skill in status.installed_skills:
        if skill == "profiles":
            continue
        table.add_row(skill, "installed")
    for skill in status.missing_skills:
        table.add_row(skill, "missing")
    console.print(table)

    profile_table = Table(title="Hermes Profiles")
    profile_table.add_column("Profile")
    profile_table.add_column("KB Root")
    profile_table.add_column("Access")
    profile_table.add_column("Read Scope")
    profile_table.add_column("Valid")
    profile_table.add_column("Message")
    for profile in status.profiles:
        profile_table.add_row(
            profile.name,
            profile.kb_root,
            profile.access_mode,
            profile.read_scope,
            str(profile.valid),
            profile.message,
        )
    console.print(profile_table)


@tags_app.command("list")
def tags_list(
    markdown_path: Annotated[Path, typer.Argument(help="Markdown file to inspect.")],
) -> None:
    """List Obsidian inline tags in a Markdown file."""

    for tag in list_tags(markdown_path):
        console.print(tag)


@tags_app.command("add")
def tags_add(
    markdown_path: Annotated[Path, typer.Argument(help="Markdown file to update.")],
    tags: Annotated[list[str] | None, typer.Option("--tag", help="Tag to add.")] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without writing.")] = False,
) -> None:
    """Add tags to the managed Obsidian tag block."""

    if not tags:
        console.print("[red]Error:[/red] provide at least one --tag")
        raise typer.Exit(code=2)
    try:
        result = add_tags_to_file(markdown_path, tags or [], dry_run=dry_run)
    except ValueError as error:
        console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(code=1) from error
    if dry_run:
        console.print(result.content)
    else:
        console.print(f"[green]Updated[/green] {result.path}")
        console.print(" ".join(result.tags))


@tags_app.command("set")
def tags_set(
    markdown_path: Annotated[Path, typer.Argument(help="Markdown file to update.")],
    tags: Annotated[list[str] | None, typer.Option("--tag", help="Tag to set.")] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without writing.")] = False,
) -> None:
    """Replace the managed Obsidian tag block."""

    if not tags:
        console.print("[red]Error:[/red] provide at least one --tag")
        raise typer.Exit(code=2)
    try:
        result = set_tags_in_file(markdown_path, tags or [], dry_run=dry_run)
    except ValueError as error:
        console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(code=1) from error
    if dry_run:
        console.print(result.content)
    else:
        console.print(f"[green]Updated[/green] {result.path}")
        console.print(" ".join(result.tags))


@index_app.command("build")
def index_build(
    kb_root: Annotated[Path, typer.Argument(help="Knowledge base root.")],
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without writing.")] = False,
) -> None:
    """Build machine-readable indexes under ai_kb/wiki/indexes."""

    result = build_indexes(kb_root, dry_run=dry_run)
    action = "Would build" if dry_run else "Built"
    console.print(f"[green]{action}[/green] indexes")
    for name, path in result.files.items():
        console.print(f"{name}: {path}")


@raw_app.command("import")
def raw_import_command(
    kb_root: Annotated[Path, typer.Argument(help="Knowledge base root.")],
    file_path: Annotated[Path, typer.Argument(help="Uploaded file to import.")],
    source_type: Annotated[
        str,
        typer.Option(
            "--source-type",
            help="Raw source type: docs, meetings, chats, web_clips, data.",
        ),
    ] = "docs",
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without writing.")] = False,
    force: Annotated[bool, typer.Option("--force", help="Overwrite an existing raw file.")] = False,
) -> None:
    """Import an uploaded file into ai_kb/raw."""

    if source_type not in RAW_SOURCE_TYPES:
        console.print(
            f"[red]Error:[/red] --source-type must be one of: {', '.join(RAW_SOURCE_TYPES)}"
        )
        raise typer.Exit(code=2)
    try:
        result = import_raw_source(
            kb_root,
            file_path,
            source_type=source_type,
            dry_run=dry_run,
            force=force,
        )
    except (FileExistsError, FileNotFoundError, ValueError) as error:
        console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(code=1) from error
    action = "Would import" if dry_run else "Imported"
    console.print(f"[green]{action}[/green] {result.relative_destination}")


@maintenance_app.command("daily")
def maintenance_daily_command(
    kb_root: Annotated[Path, typer.Argument(help="Knowledge base root.")],
    json_output: Annotated[bool, typer.Option("--json", help="Print JSON output.")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without writing.")] = False,
) -> None:
    """Run deterministic daily maintenance checks."""

    report = run_daily_maintenance(kb_root, dry_run=dry_run)
    if json_output:
        console.out(maintenance_json(report))
    else:
        console.print(maintenance_markdown(report))
