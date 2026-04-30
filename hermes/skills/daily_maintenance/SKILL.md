# daily_maintenance

## Purpose

Run deterministic daily maintenance for an LLM Wiki knowledge base.

## When to Use

Use when the user asks Hermes to check daily health, run maintenance, or decide whether anything needs ingest.

## Inputs

- Knowledge base root or configured default profile.
- Optional dry-run preference.

## Steps

1. Read the configured llm-wiki-kit Hermes profile when available.
2. Run `llm-wiki maintenance daily <kb_root>`.
3. Review new raw sources, missing source cards, manifest issues, lint issues, and recommended actions.
4. If new raw sources exist, ask whether to create source cards and ingest only those sources.
5. If no ingest is recommended, report that no re-ingest is needed.

## Safety Rules

- Must not run a daily full re-ingest.
- Must not edit, delete, rename, summarize-in-place, or move files under `ai_kb/raw/`.
- Must treat `ai_kb/wiki/indexes/` and `ai_kb/export_for_ai/` as derived outputs.
- Must not update `ai_kb/wiki/current/` unless the user explicitly confirms.

## Outputs

- Daily maintenance report.
- Recommended actions.
- New raw sources, if any.
- Lint findings, if any.
- Human review questions.

## Files It May Edit

- `ai_kb/wiki/source_manifest.md`
- `ai_kb/wiki/indexes/`

## Files It Must Not Edit

- `ai_kb/raw/`
- `ai_kb/wiki/current/`
