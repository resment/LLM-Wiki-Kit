"""Read-only installation and knowledge-base diagnostics."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from llm_wiki_kit import __version__
from llm_wiki_kit.agent_access import access_config_path
from llm_wiki_kit.linting import lint_knowledge_base
from llm_wiki_kit.manifest import manifest_source_paths
from llm_wiki_kit.source_card import source_card_path


@dataclass(frozen=True)
class DoctorCheck:
    severity: str
    code: str
    path: str
    message: str


@dataclass(frozen=True)
class DoctorReport:
    root: Path
    version: str
    checks: list[DoctorCheck]

    def to_dict(self) -> dict[str, Any]:
        return {
            "root": self.root.as_posix(),
            "version": self.version,
            "checks": [asdict(check) for check in self.checks],
            "ok": not any(check.severity == "error" for check in self.checks),
        }


REQUIRED_KB_FILES = (
    "AGENTS.md",
    "ai_kb/schema/AGENTS.md",
    "ai_kb/wiki/source_manifest.md",
)

REQUIRED_KB_DIRECTORIES = (
    "ai_kb/raw",
    "ai_kb/wiki",
    "ai_kb/wiki/source_cards",
    "ai_kb/export_for_ai",
)


def run_doctor(kb_root: Path) -> DoctorReport:
    """Run read-only diagnostics against a knowledge base."""

    root = kb_root.expanduser().resolve()
    checks: list[DoctorCheck] = [
        DoctorCheck("info", "version", "", f"llm-wiki-kit {__version__}")
    ]
    if not root.exists():
        return DoctorReport(
            root=root,
            version=__version__,
            checks=[
                *checks,
                DoctorCheck("error", "kb-root-missing", root.as_posix(), "KB root does not exist."),
            ],
        )

    for relative in REQUIRED_KB_FILES:
        _append_path_check(checks, root / relative, relative, expected="file")
    for relative in REQUIRED_KB_DIRECTORIES:
        _append_path_check(checks, root / relative, relative, expected="dir")

    if access_config_path(root).exists():
        checks.append(
            DoctorCheck(
                "info",
                "agent-access",
                ".llm-wiki/agent_access.yaml",
                "Agent access policy exists.",
            )
        )
    else:
        checks.append(
            DoctorCheck(
                "warning",
                "agent-access-missing",
                ".llm-wiki/agent_access.yaml",
                "Run llm-wiki agents wizard to configure multi-agent access.",
            )
        )

    registered = manifest_source_paths(root)
    raw_sources = _raw_sources(root)
    if raw_sources:
        checks.append(
            DoctorCheck(
                "info",
                "raw-source-count",
                "ai_kb/raw",
                f"{len(raw_sources)} raw source(s).",
            )
        )
    else:
        checks.append(DoctorCheck("info", "raw-source-count", "ai_kb/raw", "No raw sources yet."))

    missing_cards = [
        source for source in sorted(raw_sources) if not source_card_path(root, source).exists()
    ]
    if missing_cards:
        for source in missing_cards:
            checks.append(
                DoctorCheck(
                    "warning",
                    "missing-source-card",
                    source,
                    "Raw source has no source card.",
                )
            )
    else:
        checks.append(
            DoctorCheck(
                "info",
                "source-cards",
                "ai_kb/wiki/source_cards",
                "No missing source cards.",
            )
        )

    unregistered = sorted(raw_sources - registered)
    for source in unregistered:
        checks.append(
            DoctorCheck("warning", "raw-not-in-manifest", source, "Raw source is not in manifest.")
        )

    indexes_root = root / "ai_kb/wiki/indexes"
    for name in ("sources.json", "projects.json", "capabilities.json", "tags.json"):
        path = indexes_root / name
        severity = "info" if path.exists() else "warning"
        message = "Index exists." if path.exists() else "Index has not been built yet."
        checks.append(
            DoctorCheck(
                severity,
                "index-status",
                path.relative_to(root).as_posix(),
                message,
            )
        )

    for issue in lint_knowledge_base(root):
        checks.append(
            DoctorCheck(
                issue.severity,
                f"lint:{issue.code}",
                issue.path,
                issue.message,
            )
        )

    return DoctorReport(root=root, version=__version__, checks=checks)


def doctor_json(report: DoctorReport) -> str:
    return json.dumps(report.to_dict(), indent=2) + "\n"


def doctor_markdown(report: DoctorReport) -> str:
    lines = [
        "# llm-wiki-kit Doctor",
        "",
        f"- Knowledge base: `{report.root}`",
        f"- Version: `{report.version}`",
        f"- OK: `{str(report.to_dict()['ok']).lower()}`",
        "",
        "| Severity | Code | Path | Message |",
        "| --- | --- | --- | --- |",
    ]
    for check in report.checks:
        lines.append(
            f"| {check.severity} | `{check.code}` | `{check.path}` | {check.message} |"
        )
    return "\n".join(lines) + "\n"


def _append_path_check(
    checks: list[DoctorCheck],
    path: Path,
    relative: str,
    *,
    expected: str,
) -> None:
    ok = path.is_file() if expected == "file" else path.is_dir()
    if ok:
        checks.append(DoctorCheck("info", "path-ok", relative, f"Required {expected} exists."))
    else:
        checks.append(
            DoctorCheck("error", "path-missing", relative, f"Required {expected} missing.")
        )


def _raw_sources(root: Path) -> set[str]:
    raw_root = root / "ai_kb/raw"
    if not raw_root.exists():
        return set()
    return {path.relative_to(root).as_posix() for path in raw_root.rglob("*.md")}
