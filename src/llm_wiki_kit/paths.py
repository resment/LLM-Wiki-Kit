"""Canonical paths created by the Phase 1 initializer."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

KB_DIRECTORIES: tuple[str, ...] = (
    "human/inbox",
    "human/notes",
    "human/drafts",
    "ai_kb/raw/meetings",
    "ai_kb/raw/weekly",
    "ai_kb/raw/docs",
    "ai_kb/raw/chats",
    "ai_kb/raw/web_clips",
    "ai_kb/raw/data",
    "ai_kb/raw/assets",
    "ai_kb/wiki/source_cards",
    "ai_kb/wiki/portfolio",
    "ai_kb/wiki/projects",
    "ai_kb/wiki/domains",
    "ai_kb/wiki/capabilities",
    "ai_kb/wiki/concepts",
    "ai_kb/wiki/analysis",
    "ai_kb/wiki/current",
    "ai_kb/wiki/current_draft",
    "ai_kb/wiki/indexes",
    "ai_kb/schema",
    "ai_kb/export_for_ai/current",
    "ai_kb/export_for_ai/mini_kb",
    "ai_kb/export_for_ai/recent",
    "ai_kb/scripts",
    "archive",
)


@dataclass(frozen=True)
class TemplateFile:
    """A deterministic file rendered during knowledge base initialization."""

    relative_path: str
    content: str

    def destination(self, root: Path) -> Path:
        return root / self.relative_path


KB_TEMPLATE_FILES: tuple[TemplateFile, ...] = (
    TemplateFile(
        "README.md",
        """# LLM Wiki Knowledge Base

This knowledge base separates human notes, immutable raw sources, AI-compiled
wiki pages, and AI-readable exports.

## Directory Roles

- `human/`: personal writing, inbox notes, and drafts.
- `ai_kb/raw/`: immutable source files.
- `ai_kb/wiki/`: compiled knowledge pages.
- `ai_kb/schema/`: maintenance rules for agents.
- `ai_kb/export_for_ai/`: compact context for AI tools.
- `archive/`: archived material.

Review AI-generated diffs before committing changes.
""",
    ),
    TemplateFile(
        "AGENTS.md",
        """# Knowledge Base Agent Guide

## Rules

- Do not edit, delete, rename, summarize-in-place, or move files under `ai_kb/raw/`.
- Read `ai_kb/schema/AGENTS.md` before maintaining this knowledge base.
- Update `ai_kb/wiki/current_draft/` for proposed current-state changes.
- Do not update `ai_kb/wiki/current/` unless the user explicitly confirms.
- Cite source file paths for important claims.
- Treat `ai_kb/export_for_ai/` as a consumption layer, not the source of truth.
""",
    ),
    TemplateFile(
        "ai_kb/schema/AGENTS.md",
        """# LLM Wiki Maintenance Rules

## Directory Roles

- `human/`: user-authored private notes and drafts.
- `ai_kb/raw/`: immutable source of truth.
- `ai_kb/wiki/`: AI-compiled knowledge layer.
- `ai_kb/wiki/source_cards/`: structured summaries for raw sources.
- `ai_kb/wiki/current_draft/`: AI-generated current-state drafts.
- `ai_kb/wiki/current/`: human-confirmed current state.
- `ai_kb/schema/`: rules for agents.
- `ai_kb/export_for_ai/`: compact context for AI tools.

## Immutable Raw Rule

AI must never edit, delete, rename, summarize-in-place, or move files under `ai_kb/raw/`.

## Current State Rule

AI may update `current_draft/`. AI must not update `current/` unless the user explicitly confirms.

## Source Citation Rule

Every important claim in `current/` and `current_draft/` must cite at least one source file path.

## Relationship Types

- part_of
- overlaps_with
- depends_on
- informs
- conflicts_with
- supersedes
- shares_capability
- future_extension
""",
    ),
    TemplateFile(
        "ai_kb/wiki/index.md",
        """---
title: Wiki Index
---

# Wiki Index

## Navigation

- Portfolio: `portfolio/`
- Projects: `projects/`
- Domains: `domains/`
- Capabilities: `capabilities/`
- Concepts: `concepts/`
- Current drafts: `current_draft/`
- Confirmed current state: `current/`
""",
    ),
    TemplateFile(
        "ai_kb/wiki/log.md",
        """---
title: Knowledge Base Log
---

# Knowledge Base Log

| Date | Actor | Change | Notes |
| --- | --- | --- | --- |
""",
    ),
    TemplateFile(
        "ai_kb/wiki/source_manifest.md",
        """---
title: Source Manifest
---

# Source Manifest

| Source path | Date | Type | Project | Ingest status | Source card | Last updated |
| --- | --- | --- | --- | --- | --- | --- |
""",
    ),
    TemplateFile(
        "ai_kb/wiki/portfolio/projects.md",
        """---
title: Projects
---

# Projects
""",
    ),
    TemplateFile(
        "ai_kb/wiki/portfolio/capabilities.md",
        """---
title: Capabilities
---

# Capabilities
""",
    ),
    TemplateFile(
        "ai_kb/wiki/portfolio/source_trust.md",
        """---
title: Source Trust
---

# Source Trust

Use this page to describe source reliability, freshness, and review expectations.
""",
    ),
)
