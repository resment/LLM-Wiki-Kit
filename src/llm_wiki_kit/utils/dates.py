"""Date helpers."""

from __future__ import annotations

import re
from datetime import UTC, datetime

DATE_PATTERN = re.compile(r"(?P<date>\d{4}-\d{2}-\d{2})")
WEEK_PATTERN = re.compile(r"(?P<week>\d{4}-W\d{2})")


def utc_now_iso() -> str:
    """Return a stable ISO timestamp format for generated files."""

    return datetime.now(UTC).replace(microsecond=0).isoformat()


def extract_date_from_name(name: str) -> str:
    """Extract YYYY-MM-DD or YYYY-WNN from a file name."""

    date_match = DATE_PATTERN.search(name)
    if date_match:
        return date_match.group("date")
    week_match = WEEK_PATTERN.search(name)
    if week_match:
        return week_match.group("week")
    return ""
