"""Validate the bundled product knowledge operations example."""

from __future__ import annotations

import argparse
from pathlib import Path

REQUIRED_RELATIVE_PATHS = [
    "ai_kb/raw/meetings/2026-04-21_flexible-review-workflow_meeting.md",
    "ai_kb/raw/weekly/2026-W17_knowledge-portal_weekly.md",
    "ai_kb/raw/docs/2026-04-13_review-model_design.md",
    "ai_kb/wiki/source_manifest.md",
    "ai_kb/wiki/portfolio/projects.md",
    "ai_kb/wiki/portfolio/project_map.md",
    "ai_kb/wiki/portfolio/capabilities.md",
    "ai_kb/wiki/entities/aliases.md",
    "ai_kb/wiki/entities/people/alex-reviewer.md",
    "ai_kb/wiki/entities/teams/review-operations.md",
    "ai_kb/wiki/entities/product_lines/review-workflows.md",
    "ai_kb/wiki/current/core-knowledge-portal.md",
    "ai_kb/wiki/current_draft/flexible-review-workflow.md",
    "ai_kb/export_for_ai/mini_kb/flexible-review-workflow__review-prep.md",
]

FORBIDDEN_TERMS = [
    "ecommerce",
    "local life",
    "restaurant",
    "voucher",
    "checkout",
    "merchant",
]


def validate_example(example_root: Path) -> list[str]:
    """Return validation errors for an example knowledge base."""

    errors: list[str] = []
    for relative_path in REQUIRED_RELATIVE_PATHS:
        if not (example_root / relative_path).is_file():
            errors.append(f"Missing required file: {relative_path}")

    raw_files = sorted((example_root / "ai_kb/raw").rglob("*.md"))
    card_files = sorted((example_root / "ai_kb/wiki/source_cards").glob("*.source-card.md"))
    if len(raw_files) != len(card_files):
        errors.append(
            "Expected one source card per raw file: "
            f"{len(raw_files)} raw, {len(card_files)} cards"
        )

    all_text = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in example_root.rglob("*.md")
        if path.is_file()
    )
    for term in FORBIDDEN_TERMS:
        if term in all_text:
            errors.append(f"Forbidden example term remains: {term}")

    manifest = (example_root / "ai_kb/wiki/source_manifest.md").read_text(encoding="utf-8")
    for raw_file in raw_files:
        raw_relative = raw_file.relative_to(example_root).as_posix()
        if raw_relative not in manifest:
            errors.append(f"Raw file missing from manifest: {raw_relative}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a bundled Linta example.")
    parser.add_argument(
        "example_root",
        nargs="?",
        default="examples/product-knowledge-ops",
        type=Path,
    )
    args = parser.parse_args()

    errors = validate_example(args.example_root)
    if errors:
        for error in errors:
            print(error)
        return 1
    print(f"Example valid: {args.example_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
