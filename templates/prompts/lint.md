# AI Lint Prompt

You are checking semantic consistency in an LLM-compiled Markdown knowledge base.

Knowledge base root:
- {{kb_root}}

Check:
1. Project status conflicts.
2. Differences between `ai_kb/wiki/current/` and `ai_kb/wiki/current_draft/`.
3. Project relationship conflicts.
4. Capabilities referenced by multiple projects without capability pages.
5. Concepts that appear repeatedly without concept pages.
6. Current-state claims without source paths.
7. Outdated `export_for_ai/` files.
8. Expired mini-kb files.

Do not modify `ai_kb/raw/`. Output findings, affected files, and questions for human review.
