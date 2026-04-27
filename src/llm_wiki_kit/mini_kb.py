"""Mini knowledge-base draft generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from llm_wiki_kit.utils.dates import utc_now_iso
from llm_wiki_kit.utils.markdown import slugify


@dataclass(frozen=True)
class MiniKbResult:
    path: Path
    content: str
    dry_run: bool


def create_mini_kb(
    kb_root: Path,
    *,
    topic: str,
    purpose: str,
    dry_run: bool = False,
    force: bool = False,
) -> MiniKbResult:
    """Create a mini-kb draft file for an AI-assisted task."""

    root = kb_root.expanduser().resolve()
    filename = f"{slugify(topic)}__{slugify(purpose)}.md"
    output_path = root / "ai_kb/export_for_ai/mini_kb" / filename
    if output_path.exists() and not force:
        raise FileExistsError(f"Mini-kb already exists: {output_path}")

    content = render_mini_kb(topic=topic, purpose=purpose)
    if not dry_run:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
    return MiniKbResult(path=output_path, content=content, dry_run=dry_run)


def render_mini_kb(*, topic: str, purpose: str) -> str:
    return f"""# MiniKB: {topic} / {purpose}

Status as of:
Generated at: {utc_now_iso()}
Use case: {purpose}

## 1. Task Goal

## 2. Current State

Read relevant pages under `ai_kb/wiki/current/`.

## 3. Key Facts

Use source cards before raw sources.

## 4. Project Relationships

## 5. Capabilities

## 6. Open Questions

## 7. Risks / Conflicts

## 8. Reusable Talking Points

## 9. Likely Questions

## 10. Source Pages

- `ai_kb/wiki/current/`
- `ai_kb/wiki/projects/`
- `ai_kb/wiki/capabilities/`
- `ai_kb/wiki/log.md`
- `ai_kb/wiki/source_cards/`
"""
