"""Deterministic daily knowledge-base maintenance reporting."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from llm_wiki_kit.indexes import build_indexes
from llm_wiki_kit.linting import lint_knowledge_base
from llm_wiki_kit.manifest import manifest_source_paths, scan_manifest
from llm_wiki_kit.source_card import source_card_path


@dataclass(frozen=True)
class MaintenanceReport:
    root: Path
    dry_run: bool
    new_raw_sources: list[str]
    missing_source_cards: list[str]
    manifest_missing: list[str]
    lint_issues: list[dict[str, str]]
    recommended_actions: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "root": self.root.as_posix(),
            "dry_run": self.dry_run,
            "new_raw_sources": self.new_raw_sources,
            "missing_source_cards": self.missing_source_cards,
            "manifest_missing": self.manifest_missing,
            "lint_issues": self.lint_issues,
            "recommended_actions": self.recommended_actions,
        }


def run_daily_maintenance(kb_root: Path, *, dry_run: bool = False) -> MaintenanceReport:
    """Run deterministic maintenance and return a report."""

    root = kb_root.expanduser().resolve()
    registered_before = manifest_source_paths(root)
    raw_sources = _raw_markdown_sources(root)
    new_raw_sources = sorted(raw_sources - registered_before)

    scan_manifest(root, dry_run=dry_run)
    missing_source_cards = [
        source for source in sorted(raw_sources) if not source_card_path(root, source).exists()
    ]

    build_indexes(root, dry_run=dry_run)
    lint_issues = [asdict(issue) for issue in lint_knowledge_base(root)]
    manifest_missing = sorted(
        issue["path"] for issue in lint_issues if issue["code"] == "manifest-source-missing"
    )

    return MaintenanceReport(
        root=root,
        dry_run=dry_run,
        new_raw_sources=new_raw_sources,
        missing_source_cards=missing_source_cards,
        manifest_missing=manifest_missing,
        lint_issues=lint_issues,
        recommended_actions=_recommended_actions(
            new_raw_sources,
            missing_source_cards,
            lint_issues,
        ),
    )


def maintenance_json(report: MaintenanceReport) -> str:
    return json.dumps(report.to_dict(), indent=2) + "\n"


def maintenance_markdown(report: MaintenanceReport) -> str:
    lines = [
        "# Daily Maintenance Report",
        "",
        f"- Knowledge base: `{report.root}`",
        f"- Dry run: `{str(report.dry_run).lower()}`",
        "",
        "## New Raw Sources",
        "",
        *_bullet_list(report.new_raw_sources),
        "",
        "## Missing Source Cards",
        "",
        *_bullet_list(report.missing_source_cards),
        "",
        "## Manifest Missing",
        "",
        *_bullet_list(report.manifest_missing),
        "",
        "## Lint Issues",
        "",
        *_lint_list(report.lint_issues),
        "",
        "## Recommended Actions",
        "",
        *_bullet_list(report.recommended_actions),
        "",
    ]
    return "\n".join(lines)


def _raw_markdown_sources(root: Path) -> set[str]:
    raw_root = root / "ai_kb/raw"
    if not raw_root.exists():
        return set()
    return {path.relative_to(root).as_posix() for path in raw_root.rglob("*.md")}


def _recommended_actions(
    new_raw_sources: list[str],
    missing_source_cards: list[str],
    lint_issues: list[dict[str, str]],
) -> list[str]:
    actions: list[str] = []
    for source in new_raw_sources:
        actions.append(f"Create source card and ingest new raw source: {source}")
    for source in missing_source_cards:
        if source not in new_raw_sources:
            actions.append(f"Create missing source card: {source}")
    if any(issue["severity"] != "info" for issue in lint_issues):
        actions.append(
            "Review deterministic lint issues before exporting or confirming current state."
        )
    if not actions:
        actions.append("No ingest needed; knowledge base maintenance is clean.")
    return actions


def _bullet_list(items: list[str]) -> list[str]:
    if not items:
        return ["- None"]
    return [f"- `{item}`" for item in items]


def _lint_list(issues: list[dict[str, str]]) -> list[str]:
    if not issues:
        return ["- None"]
    return [
        f"- `{issue['severity']}` `{issue['code']}` `{issue['path']}`: {issue['message']}"
        for issue in issues
    ]
