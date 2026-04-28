"""Source card generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from llm_wiki_kit.utils.dates import extract_date_from_name, utc_now_iso
from llm_wiki_kit.utils.frontmatter import parse_frontmatter

REQUIRED_SOURCE_CARD_FIELDS = (
    "source_path",
    "source_date",
    "source_type",
    "direct_projects",
    "indirect_projects",
    "domains",
    "capabilities",
    "concepts",
    "ingest_status",
    "current_impact",
    "created_at",
    "updated_at",
)


@dataclass(frozen=True)
class SourceCardResult:
    path: Path
    content: str
    dry_run: bool


def source_card_path(kb_root: Path, source_path_value: str | Path) -> Path:
    """Return the deterministic source-card path for a raw source."""

    source_relative = Path(source_path_value).as_posix().removeprefix("./")
    if source_relative.startswith(str(kb_root)):
        source_relative = Path(source_relative).relative_to(kb_root).as_posix()
    raw_prefix = "ai_kb/raw/"
    if source_relative.startswith(raw_prefix):
        source_relative = source_relative.removeprefix(raw_prefix)
    card_name = source_relative.replace("/", "__").removesuffix(".md") + ".source-card.md"
    return kb_root / "ai_kb/wiki/source_cards" / card_name


def create_source_card(
    kb_root: Path,
    raw_source: Path,
    *,
    dry_run: bool = False,
    force: bool = False,
) -> SourceCardResult:
    """Create a fill-in source card template for a raw source."""

    root = kb_root.expanduser().resolve()
    source = _resolve_source(root, raw_source)
    if not _is_under(source, root / "ai_kb/raw"):
        raise ValueError(f"Source must be under ai_kb/raw: {source}")

    relative_source = source.relative_to(root).as_posix()
    card_path = source_card_path(root, relative_source)
    if card_path.exists() and not force:
        raise FileExistsError(f"Source card already exists: {card_path}")

    content = render_source_card(root, source)
    if not dry_run:
        card_path.parent.mkdir(parents=True, exist_ok=True)
        card_path.write_text(content, encoding="utf-8")
    return SourceCardResult(path=card_path, content=content, dry_run=dry_run)


def render_source_card(kb_root: Path, source: Path) -> str:
    relative_source = source.relative_to(kb_root).as_posix()
    metadata: dict[str, object] = {}
    if source.exists():
        metadata, _body = parse_frontmatter(source.read_text(encoding="utf-8"))
    now = utc_now_iso()
    source_type = metadata.get("type") or metadata.get("source_type") or source.parent.name
    source_date = metadata.get("date") or extract_date_from_name(source.name)
    return f"""---
source_path: {relative_source}
source_date: {source_date}
source_type: {source_type}
direct_projects: []
indirect_projects: []
domains: []
capabilities: []
concepts: []
ingest_status: draft
current_impact: unknown
created_at: {now}
updated_at: {now}
---

# Source Card

## Source

- `{relative_source}`

## One-line Summary

## Detailed Summary

## Confirmed Facts

## Open Questions

## Decisions

## Cross-project Impact

### Direct Projects

### Indirect Projects

### Shared Capabilities

### Concepts

## Current State Impact

## Conflicts / Risks

## Pages to Update

## Notes for Human Review
"""


def _resolve_source(root: Path, raw_source: Path) -> Path:
    if raw_source.is_absolute():
        return raw_source.resolve()
    return (root / raw_source).resolve()


def _is_under(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent.resolve())
    except ValueError:
        return False
    return True
