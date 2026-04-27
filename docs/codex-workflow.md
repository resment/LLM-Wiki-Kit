# Codex Workflow

Codex should read `AGENTS.md`, avoid raw mutations, and keep changes deterministic.

## Recommended Flow

1. Read root `AGENTS.md`.
2. For a generated knowledge base, read `ai_kb/schema/AGENTS.md`.
3. Use `llm-wiki manifest scan` and `source-card create` for deterministic setup.
4. Use `llm-wiki prompt ingest` to get task-specific instructions.
5. Edit wiki/source-card/current-draft files only as allowed by the schema rules.
6. Run `llm-wiki lint`.
7. Show changed files and human review questions.

## Constraints

- Do not call external LLM APIs in tests.
- Do not mutate `ai_kb/raw/`.
- Do not silently promote `current_draft/` to `current/`.
- Keep generated output traceable to source paths.
