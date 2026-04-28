"""Deterministic knowledge-base linting."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from llm_wiki_kit.manifest import manifest_source_paths
from llm_wiki_kit.source_card import REQUIRED_SOURCE_CARD_FIELDS, source_card_path
from llm_wiki_kit.tags import validate_managed_tag_block
from llm_wiki_kit.utils.frontmatter import has_frontmatter, parse_frontmatter
from llm_wiki_kit.utils.links import extract_markdown_links, resolve_link


@dataclass(frozen=True)
class LintIssue:
    severity: str
    code: str
    path: str
    message: str


def lint_knowledge_base(kb_root: Path, *, max_current_age: int = 30) -> list[LintIssue]:
    """Run deterministic checks against the knowledge-base structure."""

    root = kb_root.expanduser().resolve()
    issues: list[LintIssue] = []
    raw_files = sorted((root / "ai_kb/raw").rglob("*.md"))
    registered = manifest_source_paths(root)
    raw_relative = {path.relative_to(root).as_posix() for path in raw_files}

    for raw_path in raw_files:
        relative = raw_path.relative_to(root).as_posix()
        if relative not in registered:
            issues.append(
                LintIssue("error", "raw-not-in-manifest", relative, "Raw file is not registered.")
            )
        if not source_card_path(root, relative).exists():
            issues.append(
                LintIssue("warning", "missing-source-card", relative, "Source card is missing.")
            )

    for registered_path in sorted(registered - raw_relative):
        issues.append(
            LintIssue(
                "error",
                "manifest-source-missing",
                registered_path,
                "Manifest entry points to a missing raw file.",
            )
        )

    current_root = root / "ai_kb/wiki/current"
    draft_root = root / "ai_kb/wiki/current_draft"
    export_current_root = root / "ai_kb/export_for_ai/current"
    for draft in sorted(draft_root.rglob("*.md")) if draft_root.exists() else []:
        current = current_root / draft.relative_to(draft_root)
        if not current.exists():
            issues.append(
                LintIssue(
                    "warning",
                    "draft-without-current",
                    draft.relative_to(root).as_posix(),
                    "Current draft has no corresponding confirmed current page.",
                )
            )

    for current in sorted(current_root.rglob("*.md")) if current_root.exists() else []:
        relative = current.relative_to(root).as_posix()
        age_days = _age_days(current)
        if age_days > max_current_age:
            issues.append(
                LintIssue(
                    "warning",
                    "stale-current",
                    relative,
                    f"Current page is {age_days} days old.",
                )
            )
        exported = export_current_root / current.relative_to(current_root)
        if exported.exists() and exported.stat().st_mtime < current.stat().st_mtime:
            issues.append(
                LintIssue(
                    "warning",
                    "export-older-than-current",
                    exported.relative_to(root).as_posix(),
                    "Exported current page is older than its source current page.",
                )
            )

    for wiki_page in sorted((root / "ai_kb/wiki").rglob("*.md")):
        relative = wiki_page.relative_to(root).as_posix()
        text = wiki_page.read_text(encoding="utf-8")
        if "ai_kb/wiki/source_cards/" in relative:
            _extend_source_card_issues(root, wiki_page, issues)
        if not has_frontmatter(text):
            issues.append(
                LintIssue(
                    "info",
                    "missing-frontmatter",
                    relative,
                    "Wiki page does not start with YAML frontmatter.",
                )
            )
        if "raw" in wiki_page.parts:
            issues.append(
                LintIssue("error", "raw-under-wiki", relative, "Raw material is under wiki.")
            )
        _extend_link_issues(root, wiki_page, issues)
        _extend_tag_issues(root, wiki_page, issues)

    current_pages = sorted(current_root.rglob("*.md")) if current_root.exists() else []
    draft_pages = sorted(draft_root.rglob("*.md")) if draft_root.exists() else []
    for current_page in [*current_pages, *draft_pages]:
        text = current_page.read_text(encoding="utf-8")
        if "ai_kb/raw/" not in text:
            issues.append(
                LintIssue(
                    "warning",
                    "missing-source-citation",
                    current_page.relative_to(root).as_posix(),
                    "Current page does not cite an ai_kb/raw/ source path.",
                )
            )

    for directory in sorted(root.rglob("*")):
        if directory.is_dir() and _is_empty_dir(directory):
            issues.append(
                LintIssue(
                    "info",
                    "empty-directory",
                    directory.relative_to(root).as_posix(),
                    "Directory is empty.",
                )
            )

    return issues


def lint_exit_code(issues: list[LintIssue]) -> int:
    return 1 if any(issue.severity == "error" for issue in issues) else 0


def lint_json(issues: list[LintIssue]) -> str:
    return json.dumps([asdict(issue) for issue in issues], indent=2) + "\n"


def _is_empty_dir(path: Path) -> bool:
    return not any(path.iterdir())


def _age_days(path: Path) -> int:
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
    return (datetime.now(UTC) - modified).days


def _extend_source_card_issues(root: Path, source_card: Path, issues: list[LintIssue]) -> None:
    relative = source_card.relative_to(root).as_posix()
    metadata, _body = parse_frontmatter(source_card.read_text(encoding="utf-8"))
    for field in REQUIRED_SOURCE_CARD_FIELDS:
        if field not in metadata or metadata[field] in ("", None):
            issues.append(
                LintIssue("error", "source-card-missing-field", relative, f"Missing {field}.")
            )
    source_path = metadata.get("source_path")
    if isinstance(source_path, str):
        target = root / source_path
        if not source_path.startswith("ai_kb/raw/"):
            issues.append(
                LintIssue(
                    "error",
                    "source-card-source-outside-raw",
                    relative,
                    "source_path must point under ai_kb/raw/.",
                )
            )
        elif not target.exists():
            issues.append(
                LintIssue(
                    "error",
                    "source-card-source-missing",
                    relative,
                    f"source_path does not exist: {source_path}",
                )
            )


def _extend_link_issues(root: Path, page: Path, issues: list[LintIssue]) -> None:
    for link in extract_markdown_links(page):
        target = resolve_link(page, link.target, root)
        if not target.exists():
            issues.append(
                LintIssue(
                    "warning",
                    "broken-markdown-link",
                    page.relative_to(root).as_posix(),
                    f"Broken link target: {link.target}",
                )
            )


def _extend_tag_issues(root: Path, page: Path, issues: list[LintIssue]) -> None:
    for message in validate_managed_tag_block(page.read_text(encoding="utf-8")):
        issues.append(
            LintIssue(
                "warning",
                "invalid-managed-tag",
                page.relative_to(root).as_posix(),
                message,
            )
        )
