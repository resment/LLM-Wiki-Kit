# Hermes Prompt: Confirm Current

The user has explicitly approved selected draft pages for promotion to current state.

Rules:

1. Only process draft pages named by the user.
2. Do not modify `ai_kb/raw/`.
3. Preserve source citations.
4. Update corresponding pages under `ai_kb/wiki/current/`.
5. Record superseded or deferred claims.
6. Update `ai_kb/wiki/log.md`.
7. Recommend running `llm-wiki export current`.

Output current pages changed, claims promoted, claims deferred, and remaining review notes.
