"""Import uploaded files into immutable raw source folders."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path

RAW_SOURCE_TYPES = ("docs", "meetings", "chats", "web_clips", "data")


@dataclass(frozen=True)
class RawImportResult:
    root: Path
    source: Path
    destination: Path
    relative_destination: str
    dry_run: bool


def import_raw_source(
    kb_root: Path,
    file_path: Path,
    *,
    source_type: str = "docs",
    dry_run: bool = False,
    force: bool = False,
) -> RawImportResult:
    """Copy an uploaded file into ai_kb/raw/<source_type>."""

    if source_type not in RAW_SOURCE_TYPES:
        allowed = ", ".join(RAW_SOURCE_TYPES)
        raise ValueError(f"Invalid source type: {source_type}. Allowed: {allowed}")

    root = kb_root.expanduser().resolve()
    source = file_path.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Uploaded file does not exist: {source}")

    destination_dir = root / "ai_kb/raw" / source_type
    destination = destination_dir / _safe_file_name(source.name)
    if destination.exists() and not force:
        raise FileExistsError(f"Raw source already exists: {destination}")

    if not dry_run:
        destination_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    return RawImportResult(
        root=root,
        source=source,
        destination=destination,
        relative_destination=destination.relative_to(root).as_posix(),
        dry_run=dry_run,
    )


def _safe_file_name(name: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "-", name.strip()).strip(".-")
    if not sanitized:
        raise ValueError("Uploaded file must have a usable file name.")
    return sanitized
