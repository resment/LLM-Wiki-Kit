"""Obsidian inline tag helpers."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

TAG_BLOCK_START = "<!-- llm-wiki-tags:start -->"
TAG_BLOCK_END = "<!-- llm-wiki-tags:end -->"
TAG_PATTERN = re.compile(r"(?<![\w/])#([A-Za-z0-9][A-Za-z0-9_/-]*)")
TAG_BLOCK_PATTERN = re.compile(
    rf"{re.escape(TAG_BLOCK_START)}\n(?P<body>.*?)\n{re.escape(TAG_BLOCK_END)}",
    re.DOTALL,
)


@dataclass(frozen=True)
class TagWriteResult:
    path: Path
    content: str
    tags: list[str]
    dry_run: bool


def normalize_tag(value: str) -> str:
    """Normalize a user-provided value to an Obsidian inline tag."""

    raw = value.strip().removeprefix("#").strip()
    parts = [part for part in raw.split("/") if part.strip()]
    normalized_parts = [_normalize_tag_part(part) for part in parts]
    normalized = "/".join(part for part in normalized_parts if part)
    if not normalized:
        raise ValueError(f"Invalid tag: {value!r}")
    return f"#{normalized}"


def normalize_tags(values: Iterable[str]) -> list[str]:
    """Normalize and de-duplicate tags while preserving order."""

    seen: set[str] = set()
    tags: list[str] = []
    for value in values:
        tag = normalize_tag(value)
        if tag not in seen:
            seen.add(tag)
            tags.append(tag)
    return tags


def extract_inline_tags(markdown: str) -> list[str]:
    """Extract all Obsidian-style inline tags from Markdown."""

    return normalize_tags(match.group(0) for match in TAG_PATTERN.finditer(markdown))


def extract_managed_tags(markdown: str) -> list[str]:
    """Extract tags from the llm-wiki managed tag block."""

    match = TAG_BLOCK_PATTERN.search(markdown)
    if not match:
        return []
    return extract_inline_tags(match.group("body"))


def render_tag_block(tags: list[str]) -> str:
    normalized = normalize_tags(tags)
    tag_line = " ".join(normalized)
    return f"{TAG_BLOCK_START}\n{tag_line}\n{TAG_BLOCK_END}"


def add_tags_to_markdown(markdown: str, tags: list[str]) -> str:
    existing = extract_managed_tags(markdown)
    return set_tag_block(markdown, [*existing, *tags])


def set_tag_block(markdown: str, tags: list[str]) -> str:
    block = render_tag_block(tags)
    if TAG_BLOCK_PATTERN.search(markdown):
        return TAG_BLOCK_PATTERN.sub(block, markdown, count=1)
    insert_at = _tag_block_insert_offset(markdown)
    prefix = markdown[:insert_at].rstrip()
    suffix = markdown[insert_at:].lstrip("\n")
    if prefix:
        return f"{prefix}\n\n{block}\n\n{suffix}"
    return f"{block}\n\n{suffix}"


def list_tags(path: Path) -> list[str]:
    return extract_inline_tags(path.read_text(encoding="utf-8"))


def add_tags_to_file(path: Path, tags: list[str], *, dry_run: bool = False) -> TagWriteResult:
    _ensure_writable_markdown(path)
    content = path.read_text(encoding="utf-8")
    updated = add_tags_to_markdown(content, tags)
    normalized = extract_managed_tags(updated)
    if not dry_run:
        path.write_text(updated, encoding="utf-8")
    return TagWriteResult(path=path, content=updated, tags=normalized, dry_run=dry_run)


def set_tags_in_file(path: Path, tags: list[str], *, dry_run: bool = False) -> TagWriteResult:
    _ensure_writable_markdown(path)
    content = path.read_text(encoding="utf-8")
    updated = set_tag_block(content, tags)
    normalized = extract_managed_tags(updated)
    if not dry_run:
        path.write_text(updated, encoding="utf-8")
    return TagWriteResult(path=path, content=updated, tags=normalized, dry_run=dry_run)


def validate_managed_tag_block(markdown: str) -> list[str]:
    """Return validation errors for the managed tag block."""

    match = TAG_BLOCK_PATTERN.search(markdown)
    if not match:
        return []
    raw_tokens = [token for token in match.group("body").split() if token.strip()]
    errors: list[str] = []
    seen: set[str] = set()
    for token in raw_tokens:
        try:
            normalized = normalize_tag(token)
        except ValueError:
            errors.append(f"Invalid tag: {token}")
            continue
        if token != normalized:
            errors.append(f"Tag is not normalized: {token}")
        if normalized in seen:
            errors.append(f"Duplicate tag: {normalized}")
        seen.add(normalized)
    if not raw_tokens:
        errors.append("Managed tag block is empty.")
    return errors


def is_raw_path(path: Path) -> bool:
    parts = path.as_posix().split("/")
    return "ai_kb" in parts and "raw" in parts and parts.index("raw") > parts.index("ai_kb")


def _normalize_tag_part(value: str) -> str:
    part = re.sub(r"[^A-Za-z0-9_-]+", "-", value.strip().lower())
    part = part.replace("_", "-")
    part = re.sub(r"-+", "-", part).strip("-")
    return part


def _tag_block_insert_offset(markdown: str) -> int:
    if not markdown.startswith("---\n"):
        return 0
    end = markdown.find("\n---", 4)
    if end == -1:
        return 0
    end_line = markdown.find("\n", end + 4)
    return len(markdown) if end_line == -1 else end_line + 1


def _ensure_writable_markdown(path: Path) -> None:
    if is_raw_path(path):
        raise ValueError(f"Refusing to write tags into immutable raw file: {path}")
    if path.suffix.lower() != ".md":
        raise ValueError(f"Tags can only be written to Markdown files: {path}")
