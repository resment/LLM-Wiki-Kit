# Mini-KB Prompt

Create a compact mini-kb for a specific task.

Inputs:
- topic: {{topic}}
- purpose: {{purpose}}
- knowledge base root: {{kb_root}}

Read in this order:
1. `ai_kb/wiki/current/`
2. relevant project pages;
3. relevant capability pages;
4. `ai_kb/wiki/log.md`;
5. source cards;
6. raw files only when needed for verification.

Rules:
- Do not modify `ai_kb/raw/`.
- Cite source page paths.
- Separate confirmed facts from open questions.
- Include risks, conflicts, and likely questions.
- State that mini-kb output may expire.
