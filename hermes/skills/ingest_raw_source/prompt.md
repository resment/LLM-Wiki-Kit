# Hermes Prompt: Ingest Raw Source

You are maintaining an LLM-compiled Markdown knowledge base.

Read and obey:

- `AGENTS.md`
- `ai_kb/schema/AGENTS.md`

Task:

- Ingest the specified raw source under `ai_kb/raw/`.

Rules:

1. Do not modify, move, rename, or delete anything under `ai_kb/raw/`.
2. Create or update the source card.
3. Update `ai_kb/wiki/source_manifest.md`.
4. Identify direct projects, indirect projects, domains, capabilities, and concepts.
5. Update related wiki pages.
6. If current state is affected, update `ai_kb/wiki/current_draft/` only.
7. Do not update `ai_kb/wiki/current/`.
8. Update index and log.
9. Every key claim must cite a source file path.
10. Output changed files, conflicts, and human review questions.
