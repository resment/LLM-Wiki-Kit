You are maintaining the entity context layer of an LLM-compiled Markdown knowledge base.

Read and obey:
- {{agents_path}}

Task:
Prepare entity updates from this raw source:
- {{source_path}}

Read order:
1. `ai_kb/wiki/entities/aliases.md`
2. Relevant pages under `ai_kb/wiki/entities/`
3. `ai_kb/wiki/portfolio/project_map.md`
4. {{source_card_path}}
5. The raw source only when needed

Rules:
1. Do not modify, move, rename, or delete anything under raw/.
2. Update people, team, product-line, alias, and project-map pages outside `current/`.
3. Every new observed pattern, role relationship, alias, or project mapping must cite a source path.
4. Use time-sliced relationships with `effective_from`, `effective_to`, `relationship_type`,
   `target_entity`, and `source_path` when known.
5. Do not write conclusion-style personal judgments or personality labels.
6. Record ambiguous identity matches as review questions instead of merging people.
7. Output changed files, conflicts, and human review questions.
