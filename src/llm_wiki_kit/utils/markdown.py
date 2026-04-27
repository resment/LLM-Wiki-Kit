"""Markdown formatting helpers."""

from __future__ import annotations

import re


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    """Render a simple Markdown table."""

    header = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(_escape_cell(cell) for cell in row) + " |" for row in rows]
    return "\n".join([header, separator, *body])


def slugify(value: str) -> str:
    """Create a conservative file-name slug."""

    slug = re.sub(r"[^A-Za-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "untitled"


def _escape_cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")
