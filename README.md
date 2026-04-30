# llm-wiki-kit

`llm-wiki-kit` is a source-available framework for building LLM-compiled Markdown
knowledge bases.

Chinese README: [README_CN.md](README_CN.md)

It is not a normal note template and it is not a RAG system. The project separates immutable raw sources from AI-compiled wiki pages, human-confirmed current state, and export-ready context for tools such as ChatGPT, Claude, Gemini, Hermes, and Codex.

## Status

v0.2.5 provides deterministic scaffolding, initialization, manifest scanning,
source-card templates, prompt rendering, linting, current export, mini-kb draft generation,
optional Hermes skills, Obsidian-friendly Markdown tags, machine-readable indexes, and
stronger consistency checks. It also includes doctor and Hermes status diagnostics. It does not call
an LLM API by default.

## Quick Start

```bash
pip install "llm-wiki-kit @ git+https://github.com/resment/LLM-Wiki-Kit.git"
llm-wiki init ./SimonKnowledgeBase
```

For local development after cloning the repository, use `pip install -e ".[dev]"`.

## Core Layout

```text
human/                 Personal writing area. AI should not edit it by default.
ai_kb/raw/             Immutable source of truth.
ai_kb/wiki/            AI-compiled knowledge layer.
ai_kb/wiki/indexes/    Machine-readable JSON indexes.
ai_kb/schema/          Maintenance rules for agents.
ai_kb/export_for_ai/   Consumption layer for other AI tools.
archive/               Archived material.
```

## Current State

`current_draft/` is AI-generated and needs review. `current/` is the human-confirmed current state. Agents may update drafts, but must not update `current/` unless the user explicitly confirms.

## CLI

v0.2.5 supports:

```bash
llm-wiki init ./SimonKnowledgeBase
llm-wiki manifest scan ./SimonKnowledgeBase
llm-wiki manifest scan ./SimonKnowledgeBase --no-preserve-manual-fields
llm-wiki source-card create ./SimonKnowledgeBase ai_kb/raw/meetings/example.md
llm-wiki prompt ingest ./SimonKnowledgeBase ai_kb/raw/meetings/example.md
llm-wiki prompt tag ./SimonKnowledgeBase ai_kb/wiki/projects/example.md
llm-wiki tags list ./SimonKnowledgeBase/ai_kb/wiki/projects/example.md
llm-wiki tags add ./SimonKnowledgeBase/ai_kb/wiki/projects/example.md --tag project/example
llm-wiki tags set ./SimonKnowledgeBase/ai_kb/wiki/projects/example.md --tag status/draft
llm-wiki index build ./SimonKnowledgeBase
llm-wiki raw import ./SimonKnowledgeBase ~/Downloads/uploaded.md --source-type docs
llm-wiki maintenance daily ./SimonKnowledgeBase
llm-wiki doctor ./SimonKnowledgeBase
llm-wiki prompt lint-ai ./SimonKnowledgeBase
llm-wiki lint ./SimonKnowledgeBase
llm-wiki export current ./SimonKnowledgeBase
llm-wiki mini-kb create ./SimonKnowledgeBase --topic "Example" --purpose "Review prep"
llm-wiki hermes install-skills --dry-run
llm-wiki hermes status
llm-wiki hermes bootstrap-prompt ./SimonKnowledgeBase
llm-wiki hermes configure-kb ./SimonKnowledgeBase
python scripts/validate_example.py
```

Hermes integration is optional. Installed skills are prompt/procedure adapters and do not change
the deterministic CLI safety model. v0.2.1 includes Hermes tags/index skills for the existing
`llm-wiki tags` and `llm-wiki index build` workflows. v0.2.2 adds `configure-kb` so Hermes can
remember a default knowledge-base path through a local profile. v0.2.3 adds `bootstrap-prompt` so
users can paste a natural-language installation request into Hermes Agent.
v0.2.4 adds uploaded-file raw import and daily deterministic maintenance reports.
v0.2.5 adds `doctor` and `hermes status` for installation and pre-use diagnostics.

## Verify Installation

After init or Hermes setup, run:

```bash
llm-wiki doctor ./SimonKnowledgeBase
llm-wiki hermes status
```

`doctor` checks the knowledge-base layout and deterministic health. `hermes status` checks installed
skills, profiles, and whether the configured knowledge-base path is valid.

## Obsidian Tags and Indexes

`llm-wiki tags` writes controlled inline Markdown tags into wiki pages:

```md
<!-- llm-wiki-tags:start -->
#project/example #status/draft #capability/review
<!-- llm-wiki-tags:end -->
```

Tags are normalized to lowercase kebab-case and may use namespaces such as `#project/...`,
`#capability/...`, and `#status/...`. The CLI refuses to write tags into `ai_kb/raw/`; raw sources
remain immutable. `llm-wiki index build` writes JSON indexes under `ai_kb/wiki/indexes/` for tools.

## Uploads and Maintenance

For files uploaded through Hermes gateway or another chat surface, import the file into raw first:

```bash
llm-wiki raw import ./SimonKnowledgeBase ~/Downloads/uploaded.md --source-type docs
```

Daily maintenance should not re-ingest everything. Run:

```bash
llm-wiki maintenance daily ./SimonKnowledgeBase
```

The report identifies new raw sources, missing source cards, lint issues, and recommended actions.
LLM compilation remains the responsibility of the user's configured Agent environment, such as
Hermes.

## Safety Boundaries

- Raw files are immutable.
- `llm-wiki tags add/set` refuses to write inside `ai_kb/raw/`.
- Current state requires human confirmation.
- Export files are not the source of truth.
- Users should review diffs before committing generated changes.
- Tests must not call external LLM APIs.

## Licensing

llm-wiki-kit is source-available under the PolyForm Noncommercial License 1.0.0.
Noncommercial use is permitted under `LICENSE`. Commercial use requires a separate
paid commercial license; see [COMMERCIAL.md](COMMERCIAL.md).

This project is not OSI open source because commercial use is reserved.

## Hermes and Codex

Hermes integration is optional and lives under `hermes/`. It includes skills for upload import,
daily maintenance, ingest, lint, mini-kb, export, current confirmation, tags, and indexes. Codex maintenance rules live in
`AGENTS.md` and generated knowledge bases receive their own `AGENTS.md` and `ai_kb/schema/AGENTS.md`.

After installing Hermes skills, bind your default knowledge base:

```bash
llm-wiki hermes bootstrap-prompt ./SimonKnowledgeBase
llm-wiki hermes configure-kb ./SimonKnowledgeBase
```

`bootstrap-prompt` prints a natural-language prompt that Hermes Agent can follow. `configure-kb`
writes a profile under `~/.hermes/skills/llm-wiki-kit/profiles/`.

## Examples

Example projects are scaffolded under `examples/`. The `product-knowledge-ops` example includes raw
sources, source cards, portfolio pages, current/current_draft separation, and a review-prep mini-kb.

## Roadmap

See [ROADMAP.md](ROADMAP.md).

## License

PolyForm Noncommercial License 1.0.0 for noncommercial use. Commercial use requires a separate
written agreement.
