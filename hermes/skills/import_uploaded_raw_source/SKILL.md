# import_uploaded_raw_source

## Purpose

Import an uploaded file into an LLM Wiki knowledge base and prepare it for source ingestion.

## When to Use

Use when the user asks Hermes to process a file uploaded through gateway or chat.

## Inputs

- Knowledge base root or configured default profile.
- Uploaded file path.
- Source type: docs, meetings, chats, web_clips, or data.

## Steps

1. Read the configured llm-wiki-kit Hermes profile when available.
2. Run `llm-wiki raw import <kb_root> <uploaded_file> --source-type <type>`.
3. Run `llm-wiki manifest scan <kb_root>`.
4. Run `llm-wiki source-card create <kb_root> <imported_raw_path>`.
5. Use the ingest workflow only for the imported raw source.
6. Run `llm-wiki index build <kb_root>`.
7. Run `llm-wiki lint <kb_root>` and report findings.

## Safety Rules

- Must not edit, delete, rename, summarize-in-place, or move existing files under `ai_kb/raw/`.
- Must not overwrite existing raw files unless the user explicitly confirms.
- Must not do a full knowledge-base re-ingest.
- Must write proposed current-state updates to `ai_kb/wiki/current_draft/`.
- Must not update `ai_kb/wiki/current/` unless the user explicitly confirms.

## Outputs

- Imported raw source path.
- Source card path.
- Files changed.
- Lint findings, if any.
- Human review questions.

## Files It May Edit

- `ai_kb/raw/<source_type>/` for the imported file.
- `ai_kb/wiki/source_manifest.md`
- `ai_kb/wiki/source_cards/`
- Wiki pages outside `ai_kb/wiki/current/`
- `ai_kb/wiki/indexes/`

## Files It Must Not Edit

- Existing files under `ai_kb/raw/`
- `ai_kb/wiki/current/` unless explicitly confirmed.
