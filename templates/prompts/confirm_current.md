# Confirm Current Prompt

The user explicitly confirmed that selected `current_draft/` content should become current state.

Task:
Merge reviewed draft content into `ai_kb/wiki/current/`.

Rules:
1. Only process the draft pages explicitly named by the user.
2. Preserve source citations.
3. Do not modify `ai_kb/raw/`.
4. Record superseded or rejected claims when relevant.
5. Update `ai_kb/wiki/log.md`.
6. Recommend running `llm-wiki export current` after confirmation.

Output:
- current pages changed;
- draft pages processed;
- claims promoted;
- claims rejected or deferred;
- review notes.
