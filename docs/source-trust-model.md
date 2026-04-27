# Source Trust Model

Raw sources are the source of truth. Exported context is not.

## Source Classes

- Raw source: original material under `ai_kb/raw/`.
- Source card: structured summary and classification of one raw source.
- Wiki page: compiled knowledge across one or more sources.
- Current draft: AI-proposed current state.
- Current page: human-confirmed current state.
- Export: compact copy or aggregation for AI consumption.

## Trust Rules

- Prefer current pages for user-facing answers.
- Prefer source cards before opening raw files.
- Open raw files when a claim needs verification or conflict resolution.
- Treat `current_draft/` as unconfirmed.
- Treat `export_for_ai/` as stale unless its timestamp is acceptable for the task.

## Conflict Handling

Do not collapse conflicting sources into fake certainty. Record the conflict, cite the paths, and
ask for human review when the current state depends on the resolution.
