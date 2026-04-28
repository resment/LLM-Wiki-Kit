"""Deterministic raw source manifest scanning."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from llm_wiki_kit.source_card import source_card_path
from llm_wiki_kit.utils.dates import extract_date_from_name, utc_now_iso
from llm_wiki_kit.utils.frontmatter import parse_frontmatter
from llm_wiki_kit.utils.markdown import markdown_table

ManifestFormat = Literal["markdown", "json"]


@dataclass(frozen=True)
class ManifestEntry:
    source_path: str
    date: str
    source_type: str
    project: str
    ingest_status: str
    source_card_status: str
    last_updated: str


def scan_manifest(
    kb_root: Path,
    *,
    output_format: ManifestFormat = "markdown",
    dry_run: bool = False,
    preserve_manual_fields: bool = True,
) -> str:
    """Scan raw Markdown files and update source_manifest.md unless dry-run."""

    root = kb_root.expanduser().resolve()
    manifest_path = root / "ai_kb/wiki/source_manifest.md"
    entries = scan_entries(root)
    if preserve_manual_fields:
        entries = _preserve_manifest_fields(entries, read_manifest_entries(manifest_path))

    if output_format == "json":
        content = json.dumps([asdict(entry) for entry in entries], indent=2) + "\n"
    else:
        content = render_manifest(entries)

    if not dry_run and output_format == "markdown":
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(content, encoding="utf-8")

    return content


def scan_entries(kb_root: Path) -> list[ManifestEntry]:
    root = kb_root.expanduser().resolve()
    raw_root = root / "ai_kb/raw"
    return [_entry_for_source(root, path) for path in sorted(raw_root.rglob("*.md"))]


def render_manifest(entries: list[ManifestEntry]) -> str:
    rows = [
        [
            entry.source_path,
            entry.date,
            entry.source_type,
            entry.project,
            entry.ingest_status,
            entry.source_card_status,
            entry.last_updated,
        ]
        for entry in entries
    ]
    table = markdown_table(
        [
            "Source path",
            "Date",
            "Type",
            "Project",
            "Ingest status",
            "Source card",
            "Last updated",
        ],
        rows,
    )
    return f"""---
title: Source Manifest
---

# Source Manifest

{table}
"""


def manifest_source_paths(kb_root: Path) -> set[str]:
    """Read registered source paths from source_manifest.md."""

    manifest_path = kb_root / "ai_kb/wiki/source_manifest.md"
    if not manifest_path.exists():
        return set()
    paths: set[str] = set()
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| ai_kb/raw/"):
            continue
        cells = [cell.strip().replace("\\|", "|") for cell in line.strip("|").split("|")]
        if cells:
            paths.add(cells[0])
    return paths


def read_manifest_entries(manifest_path: Path) -> dict[str, ManifestEntry]:
    """Read existing manifest rows by source path."""

    if not manifest_path.exists():
        return {}
    entries: dict[str, ManifestEntry] = {}
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| ai_kb/raw/"):
            continue
        cells = [cell.strip().replace("\\|", "|") for cell in line.strip("|").split("|")]
        if len(cells) < 7:
            continue
        entry = ManifestEntry(
            source_path=cells[0],
            date=cells[1],
            source_type=cells[2],
            project=cells[3],
            ingest_status=cells[4],
            source_card_status=cells[5],
            last_updated=cells[6],
        )
        entries[entry.source_path] = entry
    return entries


def _entry_for_source(root: Path, path: Path) -> ManifestEntry:
    relative = path.relative_to(root).as_posix()
    metadata, _body = parse_frontmatter(path.read_text(encoding="utf-8"))
    source_type = str(metadata.get("type") or metadata.get("source_type") or path.parent.name)
    project_value = metadata.get("project") or metadata.get("projects") or ""
    if isinstance(project_value, list):
        project = ", ".join(str(item) for item in project_value)
    else:
        project = str(project_value)
    card_status = "exists" if source_card_path(root, relative).exists() else "missing"
    return ManifestEntry(
        source_path=relative,
        date=str(metadata.get("date") or extract_date_from_name(path.name)),
        source_type=source_type,
        project=project,
        ingest_status=str(metadata.get("ingest_status") or "new"),
        source_card_status=card_status,
        last_updated=utc_now_iso(),
    )


def _preserve_manifest_fields(
    entries: list[ManifestEntry], existing: dict[str, ManifestEntry]
) -> list[ManifestEntry]:
    preserved: list[ManifestEntry] = []
    for entry in entries:
        old = existing.get(entry.source_path)
        if not old:
            preserved.append(entry)
            continue
        preserved.append(
            ManifestEntry(
                source_path=entry.source_path,
                date=entry.date or old.date,
                source_type=entry.source_type or old.source_type,
                project=old.project or entry.project,
                ingest_status=old.ingest_status or entry.ingest_status,
                source_card_status=entry.source_card_status,
                last_updated=entry.last_updated,
            )
        )
    return preserved
