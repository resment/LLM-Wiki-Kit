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
4. Identify direct projects, indirect projects, domains, capabilities, concepts, people, teams,
   product lines, aliases, project mappings, and time-sensitive role relationships.
5. Update related wiki pages.
6. If current state is affected, update `ai_kb/wiki/current_draft/` only.
7. Do not update `ai_kb/wiki/current/`.
8. Update index and log.
9. Every key claim must cite a source file path.
10. For entity pages, write source-backed behavior patterns, concerns, decision scope,
    communication patterns, and historical cases only. Do not write conclusion-style personal
    judgments or personality labels.
11. For time-sensitive relationships, use `effective_from`, `effective_to`,
    `relationship_type`, `target_entity`, and `source_path` when known.
12. Record ambiguous identity matches as review questions instead of merging people.
13. Output changed files, conflicts, and human review questions.
