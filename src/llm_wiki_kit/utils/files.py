"""File-system helpers for deterministic initialization."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FilePlan:
    """Records what an operation created or would create."""

    directories: list[Path] = field(default_factory=list)
    files: list[Path] = field(default_factory=list)


def is_effectively_empty(path: Path) -> bool:
    """Return true when path does not exist or contains no entries."""

    if not path.exists():
        return True
    if not path.is_dir():
        return False
    return not any(path.iterdir())


def ensure_directory(path: Path, *, dry_run: bool, plan: FilePlan) -> None:
    plan.directories.append(path)
    if not dry_run:
        path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str, *, dry_run: bool, plan: FilePlan) -> None:
    plan.files.append(path)
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

