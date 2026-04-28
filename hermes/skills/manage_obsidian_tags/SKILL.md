# manage_obsidian_tags

## Purpose

Manage Obsidian-readable Markdown tags in an LLM Wiki knowledge base.

## When to Use

Use when the user asks Hermes to suggest, add, list, or replace tags on wiki Markdown pages.

## Inputs

- Knowledge base root.
- Target Markdown file path.
- Optional requested tags.
- Desired mode: list, suggest, add, or set.

## Steps

1. Read `AGENTS.md` and `ai_kb/schema/AGENTS.md`.
2. Inspect the target Markdown file and related source card when available.
3. For list mode, run `llm-wiki tags list <md_path>`.
4. For suggest mode, run or follow `llm-wiki prompt tag <kb_root> <md_path>`.
5. For add mode, run `llm-wiki tags add <md_path> --tag <tag>` for confirmed tags.
6. For set mode, run `llm-wiki tags set <md_path> --tag <tag>` for the full confirmed tag set.
7. Run `llm-wiki lint <kb_root>` after tag changes when practical.
8. Output changed files, recommended tags, and review notes.

## Safety Rules

- Must not edit, delete, rename, summarize-in-place, or move files under `ai_kb/raw/`.
- If the target file is under `ai_kb/raw/`, only list or suggest tags; do not write tags.
- Must use the managed `llm-wiki-tags` block for writes.
- Must keep tags lowercase kebab-case and prefer namespaces such as `#project/...`, `#capability/...`, and `#status/...`.
- Must not update `ai_kb/wiki/current/` unless the user explicitly asks and confirms.

## Outputs

- Current tags.
- Recommended tags.
- Files changed.
- Lint findings, if any.
- Human review notes.

## Files It May Edit

- Markdown files under `ai_kb/wiki/` except `ai_kb/wiki/current/` by default.
- Markdown files under `human/` only when explicitly requested.

## Files It Must Not Edit

- `ai_kb/raw/`
- `ai_kb/wiki/current/` unless explicitly confirmed.
