# confirm_current

## Purpose

Promote explicitly reviewed current drafts into confirmed current state.

## When to Use

Use only when the user explicitly confirms that named draft pages should become current.

## Inputs

- Knowledge base root.
- Draft page paths approved by the user.
- Optional current page targets.

## Steps

1. Read the approved draft pages.
2. Compare against corresponding current pages.
3. Preserve source citations.
4. Write confirmed content into `ai_kb/wiki/current/`.
5. Record superseded, rejected, or deferred claims.
6. Update `ai_kb/wiki/log.md`.
7. Recommend running export after confirmation.

## Safety Rules

- Must not edit `ai_kb/raw/`.
- Must edit `current/` only for user-approved draft pages.
- Must preserve source paths.
- Must not silently promote unreviewed drafts.

## Outputs

- Current pages changed.
- Draft pages processed.
- Claims promoted.
- Claims rejected or deferred.
- Human review notes.

## Files It May Edit

- `ai_kb/wiki/current/`
- `ai_kb/wiki/log.md`
- Approved files under `ai_kb/wiki/current_draft/` only if the user asks for cleanup.

## Files It Must Not Edit

- `ai_kb/raw/`
- Unapproved draft pages.
