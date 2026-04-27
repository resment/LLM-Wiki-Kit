# llm-wiki-kit

`llm-wiki-kit` is a framework for building LLM-compiled Markdown knowledge bases.

Chinese README: [README_CN.md](README_CN.md)

It is not a normal note template and it is not a RAG system. The project separates immutable raw sources from AI-compiled wiki pages, human-confirmed current state, and export-ready context for tools such as ChatGPT, Claude, Gemini, Hermes, and Codex.

## Status

v0.1 Phase 3 provides deterministic scaffolding, initialization, manifest scanning,
source-card templates, prompt rendering, linting, current export, mini-kb draft generation,
richer docs, richer templates, and an anonymized example knowledge base. It does not call an
LLM API by default.

## Quick Start

```bash
pip install -e ".[dev]"
llm-wiki init ./SimonKnowledgeBase
```

## Core Layout

```text
human/                 Personal writing area. AI should not edit it by default.
ai_kb/raw/             Immutable source of truth.
ai_kb/wiki/            AI-compiled knowledge layer.
ai_kb/schema/          Maintenance rules for agents.
ai_kb/export_for_ai/   Consumption layer for other AI tools.
archive/               Archived material.
```

## Current State

`current_draft/` is AI-generated and needs review. `current/` is the human-confirmed current state. Agents may update drafts, but must not update `current/` unless the user explicitly confirms.

## CLI

Phase 3 supports:

```bash
llm-wiki init ./SimonKnowledgeBase
llm-wiki manifest scan ./SimonKnowledgeBase
llm-wiki source-card create ./SimonKnowledgeBase ai_kb/raw/meetings/example.md
llm-wiki prompt ingest ./SimonKnowledgeBase ai_kb/raw/meetings/example.md
llm-wiki prompt lint-ai ./SimonKnowledgeBase
llm-wiki lint ./SimonKnowledgeBase
llm-wiki export current ./SimonKnowledgeBase
llm-wiki mini-kb create ./SimonKnowledgeBase --topic "Example" --purpose "Review prep"
```

Optional Hermes skill installation is planned for a later phase.

## Safety Boundaries

- Raw files are immutable.
- Current state requires human confirmation.
- Export files are not the source of truth.
- Users should review diffs before committing generated changes.
- Tests must not call external LLM APIs.

## Hermes and Codex

Hermes integration is optional and lives under `hermes/`. Codex maintenance rules live in `AGENTS.md` and generated knowledge bases receive their own `AGENTS.md` and `ai_kb/schema/AGENTS.md`.

## Examples

Example projects are scaffolded under `examples/`. The `product-knowledge-ops` example includes raw
sources, source cards, portfolio pages, current/current_draft separation, and a review-prep mini-kb.

## Roadmap

- Phase 4: optional Hermes adapter.
- Phase 5: polish, validation, and packaging hardening.

## License

MIT
