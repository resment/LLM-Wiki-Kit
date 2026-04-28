"""Markdown link extraction and resolution."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

MARKDOWN_LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\((?P<target>[^)]+)\)")
WIKI_LINK_PATTERN = re.compile(r"\[\[(?P<target>[^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")


@dataclass(frozen=True)
class LinkReference:
    source: Path
    target: str


def extract_markdown_links(path: Path) -> list[LinkReference]:
    text = path.read_text(encoding="utf-8")
    links: list[LinkReference] = []
    for match in MARKDOWN_LINK_PATTERN.finditer(text):
        target = match.group("target").strip()
        if _is_external_or_anchor(target):
            continue
        links.append(LinkReference(source=path, target=target.split("#", 1)[0]))
    for match in WIKI_LINK_PATTERN.finditer(text):
        target = match.group("target").strip()
        if target:
            links.append(LinkReference(source=path, target=target))
    return links


def resolve_link(source: Path, target: str, kb_root: Path) -> Path:
    cleaned = target.strip().removeprefix("./")
    candidate = Path(cleaned)
    if candidate.is_absolute():
        return candidate
    if (
        cleaned.startswith("ai_kb/")
        or cleaned.startswith("human/")
        or cleaned.startswith("archive/")
    ):
        return kb_root / cleaned
    if candidate.suffix:
        return source.parent / candidate
    return source.parent / f"{cleaned}.md"


def _is_external_or_anchor(target: str) -> bool:
    return (
        target.startswith("#")
        or "://" in target
        or target.startswith("mailto:")
        or target.startswith("tel:")
    )
