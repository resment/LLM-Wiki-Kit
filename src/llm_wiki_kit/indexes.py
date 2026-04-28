"""Build machine-readable indexes from deterministic knowledge-base files."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from llm_wiki_kit.manifest import scan_entries
from llm_wiki_kit.tags import extract_inline_tags
from llm_wiki_kit.utils.frontmatter import parse_frontmatter


@dataclass(frozen=True)
class IndexBuildResult:
    root: Path
    files: dict[str, Path]
    data: dict[str, Any]
    dry_run: bool


@dataclass
class NamedIndexEntry:
    name: str
    pages: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)


def build_indexes(kb_root: Path, *, dry_run: bool = False) -> IndexBuildResult:
    root = kb_root.expanduser().resolve()
    indexes_root = root / "ai_kb/wiki/indexes"
    sources = [asdict(entry) for entry in scan_entries(root)]
    projects = _named_index(root, "direct_projects", "project")
    capabilities = _named_index(root, "capabilities")
    tags = _tag_index(root)
    data: dict[str, Any] = {
        "sources": sources,
        "projects": projects,
        "capabilities": capabilities,
        "tags": tags,
    }
    files = {
        "sources": indexes_root / "sources.json",
        "projects": indexes_root / "projects.json",
        "capabilities": indexes_root / "capabilities.json",
        "tags": indexes_root / "tags.json",
    }
    if not dry_run:
        indexes_root.mkdir(parents=True, exist_ok=True)
        for name, path in files.items():
            path.write_text(
                json.dumps(data[name], indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
    return IndexBuildResult(root=root, files=files, data=data, dry_run=dry_run)


def _named_index(
    root: Path,
    list_field: str,
    scalar_field: str | None = None,
) -> list[dict[str, Any]]:
    entries: dict[str, NamedIndexEntry] = {}
    for path in sorted((root / "ai_kb/wiki").rglob("*.md")):
        metadata, _body = parse_frontmatter(path.read_text(encoding="utf-8"))
        names = _metadata_names(metadata.get(list_field))
        if scalar_field:
            names.extend(_metadata_names(metadata.get(scalar_field)))
        source_path = metadata.get("source_path")
        for name in names:
            entry = entries.setdefault(name, NamedIndexEntry(name=name))
            relative = path.relative_to(root).as_posix()
            if relative not in entry.pages:
                entry.pages.append(relative)
            if isinstance(source_path, str) and source_path not in entry.sources:
                entry.sources.append(source_path)
    return [asdict(entries[name]) for name in sorted(entries)]


def _tag_index(root: Path) -> list[dict[str, Any]]:
    entries: dict[str, list[str]] = {}
    for path in sorted((root / "ai_kb").rglob("*.md")):
        relative = path.relative_to(root).as_posix()
        for tag in extract_inline_tags(path.read_text(encoding="utf-8")):
            entries.setdefault(tag, []).append(relative)
    return [{"tag": tag, "pages": sorted(set(pages))} for tag, pages in sorted(entries.items())]


def _metadata_names(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [item.strip() for item in value.split(",") if item.strip()]
    return []
