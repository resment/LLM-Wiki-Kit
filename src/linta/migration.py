"""Rename migration helpers for Linta."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from linta.agent_access import access_config_path, legacy_access_config_path
from linta.hermes import DEFAULT_HERMES_SKILL_TARGET
from linta.tags import LEGACY_TAG_BLOCK_PATTERN, extract_managed_tags, set_tag_block

LEGACY_HERMES_SKILL_TARGET = Path.home() / ".hermes/skills/llm-wiki-kit"


@dataclass(frozen=True)
class MigrationAction:
    action: str
    status: str
    path: str
    message: str


@dataclass(frozen=True)
class MigrationReport:
    root: Path
    dry_run: bool
    actions: list[MigrationAction]

    def to_dict(self) -> dict[str, Any]:
        return {
            "root": self.root.as_posix(),
            "dry_run": self.dry_run,
            "actions": [asdict(action) for action in self.actions],
        }


def run_rename_migration(kb_root: Path, *, dry_run: bool = False) -> MigrationReport:
    root = kb_root.expanduser().resolve()
    actions: list[MigrationAction] = []

    _migrate_agent_access(root, dry_run=dry_run, actions=actions)
    _migrate_legacy_tag_blocks(root, dry_run=dry_run, actions=actions)
    _report_hermes_legacy_target(actions)

    return MigrationReport(root=root, dry_run=dry_run, actions=actions)


def migration_json(report: MigrationReport) -> str:
    return json.dumps(report.to_dict(), indent=2) + "\n"


def migration_markdown(report: MigrationReport) -> str:
    lines = [
        "# Linta Rename Migration",
        "",
        f"- Knowledge base: `{report.root}`",
        f"- Dry run: `{str(report.dry_run).lower()}`",
        "",
        "| Action | Status | Path | Message |",
        "| --- | --- | --- | --- |",
    ]
    for action in report.actions:
        lines.append(
            f"| `{action.action}` | `{action.status}` | `{action.path}` | {action.message} |"
        )
    return "\n".join(lines) + "\n"


def _migrate_agent_access(
    root: Path,
    *,
    dry_run: bool,
    actions: list[MigrationAction],
) -> None:
    legacy = legacy_access_config_path(root)
    current = access_config_path(root)
    if not legacy.exists():
        actions.append(
            MigrationAction(
                "agent-access",
                "ok" if current.exists() else "missing",
                current.relative_to(root).as_posix(),
                "Current access policy exists." if current.exists() else "No legacy policy found.",
            )
        )
        return
    if current.exists():
        actions.append(
            MigrationAction(
                "agent-access",
                "skipped",
                current.relative_to(root).as_posix(),
                "Current policy already exists; legacy policy left untouched.",
            )
        )
        return
    actions.append(
        MigrationAction(
            "agent-access",
            "would-copy" if dry_run else "copied",
            current.relative_to(root).as_posix(),
            "Copy legacy .llm-wiki policy to .linta policy path.",
        )
    )
    if not dry_run:
        current.parent.mkdir(parents=True, exist_ok=True)
        current.write_text(legacy.read_text(encoding="utf-8"), encoding="utf-8")


def _migrate_legacy_tag_blocks(
    root: Path,
    *,
    dry_run: bool,
    actions: list[MigrationAction],
) -> None:
    wiki_root = root / "ai_kb/wiki"
    if not wiki_root.exists():
        actions.append(
            MigrationAction("tag-blocks", "missing", "ai_kb/wiki", "Wiki directory missing.")
        )
        return
    changed = 0
    for path in sorted(wiki_root.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        if not LEGACY_TAG_BLOCK_PATTERN.search(text):
            continue
        updated = set_tag_block(text, extract_managed_tags(text))
        changed += 1
        actions.append(
            MigrationAction(
                "tag-block",
                "would-update" if dry_run else "updated",
                path.relative_to(root).as_posix(),
                "Replace legacy llm-wiki-tags block with linta-tags block.",
            )
        )
        if not dry_run:
            path.write_text(updated, encoding="utf-8")
    if changed == 0:
        actions.append(
            MigrationAction("tag-blocks", "ok", "ai_kb/wiki", "No legacy tag blocks found.")
        )


def _report_hermes_legacy_target(actions: list[MigrationAction]) -> None:
    if LEGACY_HERMES_SKILL_TARGET.exists() and not DEFAULT_HERMES_SKILL_TARGET.exists():
        actions.append(
            MigrationAction(
                "hermes-skills",
                "manual",
                LEGACY_HERMES_SKILL_TARGET.as_posix(),
                "Legacy Hermes skill directory exists; run linta hermes install-skills.",
            )
        )
        return
    if DEFAULT_HERMES_SKILL_TARGET.exists():
        actions.append(
            MigrationAction(
                "hermes-skills",
                "ok",
                DEFAULT_HERMES_SKILL_TARGET.as_posix(),
                "Current Hermes skill directory exists.",
            )
        )
        return
    actions.append(
        MigrationAction(
            "hermes-skills",
            "missing",
            DEFAULT_HERMES_SKILL_TARGET.as_posix(),
            "No Linta Hermes skill directory found.",
        )
    )
