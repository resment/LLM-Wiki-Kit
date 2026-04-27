# export_for_ai

## Purpose

Prepare compact AI-consumable context from confirmed knowledge.

## When to Use

Use after current pages are confirmed or when the user needs context for another AI tool.

## Inputs

- Knowledge base root.
- Optional export scope.

## Steps

1. Read confirmed pages under `ai_kb/wiki/current/`.
2. Preserve source citations.
3. Generate or update files under `ai_kb/export_for_ai/current/`.
4. Record export time and included pages.
5. Report stale or missing current pages.

## Safety Rules

- Must not edit `ai_kb/raw/`.
- Must not read `current_draft/` as confirmed state.
- Must not invent missing current state.

## Outputs

- Exported files.
- Included source pages.
- Freshness notes.
- Human review questions.

## Files It May Edit

- `ai_kb/export_for_ai/current/`
- `ai_kb/wiki/log.md`

## Files It Must Not Edit

- `ai_kb/raw/`
- `ai_kb/wiki/current/`
- `ai_kb/wiki/current_draft/`
