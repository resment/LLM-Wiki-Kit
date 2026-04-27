"""Knowledge base initialization."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from llm_wiki_kit.paths import KB_DIRECTORIES, KB_TEMPLATE_FILES
from llm_wiki_kit.utils.files import FilePlan, ensure_directory, is_effectively_empty, write_text


class InitError(RuntimeError):
    """Raised when a knowledge base cannot be initialized safely."""


@dataclass(frozen=True)
class InitResult:
    """Result of an initialization run."""

    root: Path
    dry_run: bool
    plan: FilePlan


def init_knowledge_base(target: Path, *, dry_run: bool = False, force: bool = False) -> InitResult:
    """Create a deterministic LLM Wiki knowledge base skeleton."""

    root = target.expanduser().resolve()
    if root.exists() and not root.is_dir():
        raise InitError(f"Target exists and is not a directory: {root}")

    if root.exists() and not force and not is_effectively_empty(root):
        raise InitError(
            f"Target directory is not empty: {root}. Use --force to write templates there."
        )

    plan = FilePlan()
    ensure_directory(root, dry_run=dry_run, plan=plan)

    for directory in KB_DIRECTORIES:
        ensure_directory(root / directory, dry_run=dry_run, plan=plan)

    for template in KB_TEMPLATE_FILES:
        write_text(template.destination(root), template.content, dry_run=dry_run, plan=plan)

    return InitResult(root=root, dry_run=dry_run, plan=plan)

