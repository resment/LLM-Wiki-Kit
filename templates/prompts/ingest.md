You are maintaining an LLM-compiled Markdown knowledge base.

Read and obey:
- {{agents_path}}

Task:
Ingest this raw source:
- {{source_path}}

Rules:
1. Do not modify, move, rename, or delete anything under raw/.
2. Create or update the source card at {{source_card_path}}.
3. Update {{source_manifest_path}}.
4. Identify direct projects, indirect projects, domains, capabilities, and concepts.
5. Update related wiki pages.
6. If current state is affected, update current_draft only.
7. Do not update current unless explicitly instructed.
8. Update index and log.
9. Update export_for_ai if appropriate.
10. Every key claim must cite source file path.
11. Output files changed, new pages, current_draft changes, conflicts, and review questions.

