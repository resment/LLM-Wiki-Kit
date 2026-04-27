# Hermes Prompt: Lint Knowledge Base

Check this LLM Wiki knowledge base for semantic consistency.

Check:

1. Project status conflicts.
2. Differences between `current/` and `current_draft/`.
3. Missing source cards.
4. Current-state claims without source paths.
5. Capabilities referenced by multiple projects without capability pages.
6. Concepts repeatedly referenced without concept pages.
7. Outdated exports or mini-kbs.

Do not modify `ai_kb/raw/`.
Do not update `ai_kb/wiki/current/`.

Output findings, affected files, suggested fixes, and human review questions.
