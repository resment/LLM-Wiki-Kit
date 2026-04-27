# Mini-KB

A mini-kb is a task-specific context package under `ai_kb/export_for_ai/mini_kb/`.

Use it when a user needs compact context for a meeting, review, report, voice session, or temporary
AI chat.

## Create

```bash
llm-wiki mini-kb create ./YourKnowledgeBase --topic "Example Project" --purpose "Review prep"
```

The generated file is a draft shell. It points the agent toward:

- confirmed current pages;
- project pages;
- capability pages;
- recent log entries;
- source cards.

## Expiration

Mini-kbs are snapshots. They may become stale when current pages or source cards change. Treat them
as convenient context, not as source of truth.
