"""Export helpers for confirmed current state."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from llm_wiki_kit.utils.dates import utc_now_iso


@dataclass(frozen=True)
class ExportResult:
    files: list[Path]


def export_current(
    kb_root: Path,
    *,
    single_file: str | None = None,
    dry_run: bool = False,
) -> ExportResult:
    """Copy confirmed current pages into export_for_ai/current."""

    root = kb_root.expanduser().resolve()
    current_root = root / "ai_kb/wiki/current"
    export_root = root / "ai_kb/export_for_ai/current"
    generated: list[Path] = []
    timestamp = utc_now_iso()

    current_files = sorted(current_root.rglob("*.md")) if current_root.exists() else []
    if not dry_run:
        export_root.mkdir(parents=True, exist_ok=True)

    for source in current_files:
        target = export_root / source.relative_to(current_root)
        generated.append(target)
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    readme = export_root / "README.md"
    generated.append(readme)
    readme_content = render_export_readme(timestamp, current_files)
    if not dry_run:
        readme.write_text(readme_content, encoding="utf-8")

    if single_file:
        single_path = export_root / single_file
        generated.append(single_path)
        content = render_single_file(timestamp, current_root, current_files)
        if not dry_run:
            single_path.write_text(content, encoding="utf-8")

    return ExportResult(files=generated)


def render_export_readme(timestamp: str, current_files: list[Path]) -> str:
    rows = "\n".join(f"- `{path.name}`" for path in current_files) or "- No current pages found."
    return f"""# Current State Export

Exported at: {timestamp}

This folder is generated from confirmed pages under `ai_kb/wiki/current/`.
It is a consumption layer, not the source of truth.

## Files

{rows}
"""


def render_single_file(timestamp: str, current_root: Path, current_files: list[Path]) -> str:
    sections = [
        "# Current State Export",
        "",
        f"Exported at: {timestamp}",
        "",
    ]
    for source in current_files:
        relative = source.relative_to(current_root).as_posix()
        sections.extend(
            [
                f"## {relative}",
                "",
                source.read_text(encoding="utf-8"),
                "",
            ]
        )
    return "\n".join(sections)
