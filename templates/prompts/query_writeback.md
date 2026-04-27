# Query Writeback Prompt

The user asked a high-value question whose answer should be preserved.

Task:
Write the conclusion back to `ai_kb/wiki/analysis/`.

Rules:
1. Read current pages first.
2. Read source cards before raw files.
3. Cite source paths for important claims.
4. Do not modify `ai_kb/raw/`.
5. Do not update `current/` unless explicitly confirmed.
6. If the answer changes current state, update `current_draft/`.

Output:
- analysis page created or updated;
- source paths used;
- current_draft changes, if any;
- unresolved questions.
