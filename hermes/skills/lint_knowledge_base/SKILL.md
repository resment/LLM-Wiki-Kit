# lint_knowledge_base

## Purpose

Review deterministic and semantic consistency in an LLM Wiki knowledge base.

## When to Use

Use before committing knowledge-base changes or when the user asks for a consistency review.

## Inputs

- Knowledge base root.
- Optional focus area.

## Steps

1. Run or inspect deterministic lint output when available.
2. Read `ai_kb/wiki/index.md`.
3. Compare `current/` and `current_draft/`.
4. Check project, capability, and concept consistency.
5. Check source cards and source citations.
6. Report findings by severity.

## Safety Rules

- Must not edit `ai_kb/raw/`.
- Should not edit files by default; report findings first.
- Must not update `current/`.

## Outputs

- Findings.
- Affected files.
- Suggested fixes.
- Human review questions.

## Files It May Edit

- None by default.
- If explicitly asked to fix: wiki pages outside `ai_kb/raw/` and outside `current/`.

## Files It Must Not Edit

- `ai_kb/raw/`
- `ai_kb/wiki/current/`
