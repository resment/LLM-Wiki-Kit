# Hermes Prompt: Export for AI

Prepare AI-consumable context from confirmed current pages.

Rules:

1. Read `ai_kb/wiki/current/`.
2. Do not use `current_draft/` as confirmed state.
3. Do not modify `ai_kb/raw/`.
4. Preserve source citations.
5. Write export files under `ai_kb/export_for_ai/current/`.
6. State export time, included pages, and stale context.

Output exported files and review questions.
