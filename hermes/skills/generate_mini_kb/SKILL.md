# generate_mini_kb

## Purpose

Create or fill a task-specific mini-kb for a meeting, review, report, or temporary AI session.

## When to Use

Use when the user provides a topic and purpose and needs compact context.

## Inputs

- Knowledge base root.
- Topic.
- Purpose.
- Optional target mini-kb path.

## Steps

1. Read current pages first.
2. Read relevant project and capability pages.
3. Read recent log entries.
4. Read source cards before raw sources.
5. Create or update a mini-kb under `ai_kb/export_for_ai/mini_kb/`.
6. Separate confirmed facts from open questions.

## Safety Rules

- Must not edit `ai_kb/raw/`.
- Must not update `current/`.
- Must cite source page paths.
- Must state that mini-kb output may expire.

## Outputs

- Mini-kb file path.
- Source pages used.
- Open questions.
- Expiration or freshness notes.

## Files It May Edit

- `ai_kb/export_for_ai/mini_kb/`
- `ai_kb/wiki/log.md`

## Files It Must Not Edit

- `ai_kb/raw/`
- `ai_kb/wiki/current/`
