# Current State Workflow

Use `current_draft/` for AI-generated updates and `current/` for human-confirmed state.

## Draft Rules

Agents may update `ai_kb/wiki/current_draft/` when a source affects active status, decisions,
risks, ownership, scope, or timeline. Drafts must cite source paths.

## Confirmation Rules

Agents must not update `ai_kb/wiki/current/` unless the user explicitly asks for confirmation or
promotion. A confirmation workflow should:

1. Compare draft and current.
2. Preserve source citations.
3. Record superseded or rejected claims.
4. Update `log.md`.
5. Regenerate `export_for_ai/current/` if needed.

## Staleness

`llm-wiki lint --max-current-age N` warns when current pages have not been updated recently. This
does not mean the page is wrong; it means the user should review freshness.
