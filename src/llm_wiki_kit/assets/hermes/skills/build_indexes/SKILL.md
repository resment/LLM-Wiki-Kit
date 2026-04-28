# build_indexes

## Purpose

Build machine-readable JSON indexes for an LLM Wiki knowledge base.

## When to Use

Use after ingesting sources, editing wiki pages, changing tags, or before exporting context to other AI tools.

## Inputs

- Knowledge base root.
- Optional dry-run preference.

## Steps

1. Read `AGENTS.md` and `ai_kb/schema/AGENTS.md`.
2. Run `llm-wiki lint <kb_root>` before building when practical.
3. Run `llm-wiki index build <kb_root>` or `llm-wiki index build <kb_root> --dry-run`.
4. Inspect generated files under `ai_kb/wiki/indexes/`.
5. Report index files written and any lint issues that should be reviewed.

## Safety Rules

- Must not edit, delete, rename, summarize-in-place, or move files under `ai_kb/raw/`.
- Must treat indexes as derived artifacts, not source of truth.
- Must not manually edit generated JSON indexes unless explicitly debugging generation output.
- Must not update `ai_kb/wiki/current/`.

## Outputs

- Index files built.
- Lint findings, if any.
- Source files or wiki pages that appear inconsistent.
- Human review notes.

## Files It May Edit

- `ai_kb/wiki/indexes/sources.json`
- `ai_kb/wiki/indexes/projects.json`
- `ai_kb/wiki/indexes/capabilities.json`
- `ai_kb/wiki/indexes/tags.json`

## Files It Must Not Edit

- `ai_kb/raw/`
- `ai_kb/wiki/current/`
