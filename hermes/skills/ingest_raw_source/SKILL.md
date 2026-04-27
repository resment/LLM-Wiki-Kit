# ingest_raw_source

## Purpose

Compile one raw source into the LLM Wiki knowledge layer.

## When to Use

Use when the user asks Hermes to ingest a new or existing file under `ai_kb/raw/`.

## Inputs

- Knowledge base root.
- Raw source path under `ai_kb/raw/`.
- Optional existing source card path.

## Steps

1. Read `AGENTS.md` and `ai_kb/schema/AGENTS.md`.
2. Read the raw source.
3. Create or update the source card.
4. Update `ai_kb/wiki/source_manifest.md`.
5. Update related project, capability, concept, or analysis pages.
6. Update `ai_kb/wiki/current_draft/` only when current state is affected.
7. Update `ai_kb/wiki/index.md` and `ai_kb/wiki/log.md`.
8. Output changed files and human review questions.

## Safety Rules

- Must not edit, delete, rename, summarize-in-place, or move files under `ai_kb/raw/`.
- Must not update `ai_kb/wiki/current/`.
- Must cite source file paths for important claims.
- Must preserve unresolved conflicts.

## Outputs

- Files changed.
- Pages created.
- Current draft changes.
- Conflicts found.
- Questions for human review.

## Files It May Edit

- `ai_kb/wiki/source_cards/`
- `ai_kb/wiki/source_manifest.md`
- `ai_kb/wiki/projects/`
- `ai_kb/wiki/domains/`
- `ai_kb/wiki/capabilities/`
- `ai_kb/wiki/concepts/`
- `ai_kb/wiki/analysis/`
- `ai_kb/wiki/current_draft/`
- `ai_kb/wiki/index.md`
- `ai_kb/wiki/log.md`

## Files It Must Not Edit

- `ai_kb/raw/`
- `ai_kb/wiki/current/`
