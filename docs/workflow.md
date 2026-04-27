# Workflow

## 1. Add Raw Sources

Place source material under `ai_kb/raw/`. Use subfolders such as `meetings/`, `weekly/`, `docs/`,
`chats/`, and `web_clips/`. Raw files are immutable once added.

## 2. Register Sources

Run:

```bash
llm-wiki manifest scan ./YourKnowledgeBase
```

This updates `ai_kb/wiki/source_manifest.md` from file paths and frontmatter.

## 3. Create Source Cards

Run:

```bash
llm-wiki source-card create ./YourKnowledgeBase ai_kb/raw/meetings/example.md
```

The generated card is a structured shell for an agent or human to fill.

## 4. Compile Wiki Pages

Use `llm-wiki prompt ingest` to produce instructions for Codex, Hermes, Claude Code, or another
agent. The prompt tells the agent to update wiki pages, source cards, manifest, log, and
`current_draft/` when appropriate.

## 5. Confirm Current State

Review `current_draft/` manually. Only promote content into `current/` after explicit confirmation.

## 6. Export for AI

Run `llm-wiki export current` to prepare compact, confirmed context for other AI tools.
