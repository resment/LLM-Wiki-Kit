"""Minimal YAML frontmatter helpers."""

from __future__ import annotations

from typing import Any

import yaml


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Return frontmatter metadata and body from a Markdown document."""

    if not text.startswith("---\n"):
        return {}, text
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return {}, text
    raw_metadata = yaml.safe_load(parts[1]) or {}
    if not isinstance(raw_metadata, dict):
        return {}, parts[2]
    return raw_metadata, parts[2]


def has_frontmatter(text: str) -> bool:
    """Return true if a Markdown document starts with YAML frontmatter."""

    metadata, _body = parse_frontmatter(text)
    return bool(metadata) or text.startswith("---\n")
