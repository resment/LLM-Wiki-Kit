"""Build machine-readable indexes from deterministic knowledge-base files."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from linta.manifest import scan_entries
from linta.tags import extract_inline_tags
from linta.utils.frontmatter import parse_frontmatter


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
    entities = _entity_index(root)
    relationships = _relationship_index(root)
    project_map = _project_map_index(root)
    data: dict[str, Any] = {
        "sources": sources,
        "projects": projects,
        "capabilities": capabilities,
        "tags": tags,
        "entities": entities,
        "relationships": relationships,
        "project_map": project_map,
    }
    files = {
        "sources": indexes_root / "sources.json",
        "projects": indexes_root / "projects.json",
        "capabilities": indexes_root / "capabilities.json",
        "tags": indexes_root / "tags.json",
        "entities": indexes_root / "entities.json",
        "relationships": indexes_root / "relationships.json",
        "project_map": indexes_root / "project_map.json",
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


def _entity_index(root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for path in _entity_pages(root):
        metadata, _body = parse_frontmatter(path.read_text(encoding="utf-8"))
        entity_type = str(metadata.get("entity_type") or _entity_type_from_path(path))
        entity_id = str(metadata.get("entity_id") or path.stem).strip()
        if path.name.startswith("_") or not entity_id:
            continue
        entries.append(
            {
                "entity_id": entity_id,
                "entity_type": entity_type,
                "name": str(metadata.get("title") or entity_id),
                "aliases": _metadata_names(metadata.get("aliases")),
                "page": path.relative_to(root).as_posix(),
            }
        )
    return sorted(entries, key=lambda item: (item["entity_type"], item["entity_id"]))


def _relationship_index(root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for path in _entity_pages(root):
        metadata, _body = parse_frontmatter(path.read_text(encoding="utf-8"))
        source_entity = str(metadata.get("entity_id") or path.stem).strip()
        if path.name.startswith("_") or not source_entity:
            continue
        for relationship in _dict_list(metadata.get("relationships")):
            entry = {
                "source_entity": source_entity,
                "source_entity_type": str(
                    metadata.get("entity_type") or _entity_type_from_path(path)
                ),
                "page": path.relative_to(root).as_posix(),
            }
            entry.update({str(key): _json_value(value) for key, value in relationship.items()})
            entries.append(entry)
    return sorted(
        entries,
        key=lambda item: (
            str(item.get("source_entity") or ""),
            str(item.get("relationship_type") or ""),
            str(item.get("target_entity") or ""),
        ),
    )


def _project_map_index(root: Path) -> list[dict[str, Any]]:
    path = root / "ai_kb/wiki/portfolio/project_map.md"
    if not path.exists():
        return []
    metadata, _body = parse_frontmatter(path.read_text(encoding="utf-8"))
    projects = _dict_list(metadata.get("projects"))
    return [
        {
            "project": str(project.get("project") or project.get("name") or ""),
            "aliases": _metadata_names(project.get("aliases")),
            "related_people": _metadata_names(project.get("related_people")),
            "related_teams": _metadata_names(project.get("related_teams")),
            "current_phase": str(project.get("current_phase") or project.get("phase") or ""),
            "possible_blockers": _metadata_names(project.get("possible_blockers")),
            "historical_controversy_points": _metadata_names(
                project.get("historical_controversy_points")
            ),
            "sources": _metadata_names(project.get("sources")),
        }
        for project in projects
        if str(project.get("project") or project.get("name") or "").strip()
    ]


def _metadata_names(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if not isinstance(item, dict) and str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [item.strip() for item in value.split(",") if item.strip()]
    return []


def _dict_list(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _json_value(value: object) -> object:
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if value is None or isinstance(value, str | int | float | bool):
        return value
    return str(value)


def _entity_pages(root: Path) -> list[Path]:
    entities_root = root / "ai_kb/wiki/entities"
    if not entities_root.exists():
        return []
    return sorted(path for path in entities_root.rglob("*.md") if path.name != "aliases.md")


def _entity_type_from_path(path: Path) -> str:
    parent = path.parent.name
    if parent == "people":
        return "person"
    if parent == "teams":
        return "team"
    if parent == "product_lines":
        return "product_line"
    return "entity"
