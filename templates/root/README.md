# LLM Wiki Knowledge Base

This knowledge base separates human notes, immutable raw sources, AI-compiled wiki pages,
human-confirmed current state, and AI-readable exports.

## Start Here

- Human notes: `human/`
- Immutable sources: `ai_kb/raw/`
- Compiled wiki: `ai_kb/wiki/`
- Agent rules: `ai_kb/schema/AGENTS.md`
- AI exports: `ai_kb/export_for_ai/`

## Rules

- Do not edit files under `ai_kb/raw/`.
- Use `ai_kb/wiki/current_draft/` for proposed current-state changes.
- Use `ai_kb/wiki/current/` only for human-confirmed state.
- Keep source paths attached to important claims.
- Treat exports and mini-kbs as consumable snapshots, not source of truth.
