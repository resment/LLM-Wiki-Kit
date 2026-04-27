# LLM Wiki Maintenance Rules

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

AI may update `current_draft/`.
AI must not update `current/` unless the user explicitly confirms.

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

## Ingest Workflow

1. Read the raw source.
2. Identify date, type, direct projects, indirect projects, domains, capabilities, concepts.
3. Create or update source card.
4. Update source_manifest.
5. Update related wiki pages.
6. Update current_draft only if current state is affected.
7. Update index and log.
8. Update export_for_ai if appropriate.
9. Output changes and human review questions.

## Query Workflow

1. Read index and relevant current pages first.
2. Read project, capability, and concept pages as needed.
3. Read source cards before raw.
4. Read raw only when necessary.
5. State the effective date.
6. Do not merge conflicting materials into fake certainty.

## Lint Workflow

Check stale current pages, unreviewed current_draft, missing source cards, missing citations,
conflicting status, orphan pages, and outdated export files.
