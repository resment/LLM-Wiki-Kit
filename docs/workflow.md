# Workflow

## 1. Add Raw Sources

Place source material under `ai_kb/raw/`. Use subfolders such as `meetings/`, `weekly/`, `docs/`,
`chats/`, and `web_clips/`. Raw files are immutable once added.

## 2. Register Sources

Run:

```bash
linta manifest scan ./YourKnowledgeBase
```

This updates `ai_kb/wiki/source_manifest.md` from file paths and frontmatter.

## 3. Create Source Cards

Run:

```bash
linta source-card create ./YourKnowledgeBase ai_kb/raw/meetings/example.md
```

The generated card is a structured shell for an agent or human to fill.

## 4. Compile Wiki Pages

Use `linta prompt ingest` to produce instructions for Codex, Hermes, Claude Code, or another
agent. The prompt tells the agent to update wiki pages, source cards, manifest, log, and
`current_draft/` when appropriate.

For focused entity maintenance, use `linta prompt entities <kb_root> <raw_source>`. This prompt
asks the agent to update compiled people, team, product-line, alias, and project-map context while
keeping semantic extraction source-backed and outside `ai_kb/wiki/current/`.

## 5. Add Reading Tags

Use `linta tags add` or `linta tags set` on wiki Markdown pages to add Obsidian-readable
inline tags. The command writes a managed block in the Markdown body and refuses to write under
`ai_kb/raw/`.

```bash
linta tags add ./YourKnowledgeBase/ai_kb/wiki/projects/example.md --tag project/example
linta prompt tag ./YourKnowledgeBase ai_kb/wiki/projects/example.md
```

## 6. Build Indexes

Run:

```bash
linta index build ./YourKnowledgeBase
```

Indexes are written under `ai_kb/wiki/indexes/` for tools. They include source, project,
capability, tag, entity, relationship, and project-map indexes. They are derived artifacts, not the
source of truth.

## 7. Confirm Current State

Review `current_draft/` manually. Only promote content into `current/` after explicit confirmation.

## 8. Export for AI

Run `linta export current` to prepare compact, confirmed context for other AI tools.
