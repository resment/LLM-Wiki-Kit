# Hermes Prompt: Generate Mini-KB

Create a compact mini-kb for the requested topic and purpose.

Read in this order:

1. `ai_kb/wiki/current/`
2. Relevant project pages.
3. Relevant capability pages.
4. `ai_kb/wiki/log.md`.
5. Source cards.
6. Raw files only when necessary for verification.

Rules:

- Do not modify `ai_kb/raw/`.
- Do not update `ai_kb/wiki/current/`.
- Cite source page paths.
- Separate confirmed facts, open questions, risks, and conflicts.
- State that the mini-kb may expire.
