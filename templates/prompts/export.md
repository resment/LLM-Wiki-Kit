# Export Prompt

You are preparing AI-consumable context from an LLM Wiki knowledge base.

Rules:
1. Read confirmed pages under `ai_kb/wiki/current/`.
2. Do not read `ai_kb/wiki/current_draft/` unless asked to compare freshness.
3. Do not read or modify `ai_kb/raw/`.
4. Preserve source citations.
5. State export time and effective date.
6. Flag stale or missing current pages instead of filling gaps from memory.

Output:
- files created or updated;
- pages included;
- stale or missing context;
- questions for human review.
