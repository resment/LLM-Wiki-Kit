# Linta（灵台）

`Linta`（中文名：灵台） is a source-available framework for building LLM-compiled Markdown
knowledge bases.

Chinese README: [README_CN.md](README_CN.md)

It is not a normal note template and it is not a RAG system. The project separates immutable raw sources from AI-compiled wiki pages, human-confirmed current state, and export-ready context for tools such as ChatGPT, Claude, Gemini, Hermes, and Codex.

## Status

v0.3.2 provides deterministic scaffolding, initialization, manifest scanning,
source-card templates, prompt rendering, linting, current export, mini-kb draft generation,
optional Hermes skills, Obsidian-friendly Markdown tags, machine-readable indexes, and
stronger consistency checks. It also includes doctor diagnostics, Hermes status, multi-agent access
profiles, and a Claude Desktop read-only MCP adapter. It does not call an LLM API by default.

## Quick Start

```bash
pip install "linta @ git+https://github.com/resment/Linta.git"
linta init ./SimonKnowledgeBase
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

v0.3.2 supports:

```bash
linta init ./SimonKnowledgeBase
linta manifest scan ./SimonKnowledgeBase
linta manifest scan ./SimonKnowledgeBase --no-preserve-manual-fields
linta source-card create ./SimonKnowledgeBase ai_kb/raw/meetings/example.md
linta prompt ingest ./SimonKnowledgeBase ai_kb/raw/meetings/example.md
linta prompt tag ./SimonKnowledgeBase ai_kb/wiki/projects/example.md
linta tags list ./SimonKnowledgeBase/ai_kb/wiki/projects/example.md
linta tags add ./SimonKnowledgeBase/ai_kb/wiki/projects/example.md --tag project/example
linta tags set ./SimonKnowledgeBase/ai_kb/wiki/projects/example.md --tag status/draft
linta index build ./SimonKnowledgeBase
linta raw import ./SimonKnowledgeBase ~/Downloads/uploaded.md --source-type docs
linta maintenance daily ./SimonKnowledgeBase
linta doctor ./SimonKnowledgeBase
linta migrate ./SimonKnowledgeBase --dry-run
linta agents wizard ./SimonKnowledgeBase
linta agents status ./SimonKnowledgeBase
linta claude-desktop config ./SimonKnowledgeBase
linta claude-desktop status ./SimonKnowledgeBase
linta mcp serve --agent claude-desktop --kb-root ./SimonKnowledgeBase
linta prompt lint-ai ./SimonKnowledgeBase
linta lint ./SimonKnowledgeBase
linta export current ./SimonKnowledgeBase
linta mini-kb create ./SimonKnowledgeBase --topic "Example" --purpose "Review prep"
linta hermes install-skills --dry-run
linta hermes status
linta hermes bootstrap-prompt ./SimonKnowledgeBase
linta hermes configure-kb ./SimonKnowledgeBase
python scripts/validate_example.py
```

Hermes integration is optional. Installed skills are prompt/procedure adapters and do not change
the deterministic CLI safety model. v0.2.1 includes Hermes tags/index skills for the existing
`linta tags` and `linta index build` workflows. v0.2.2 adds `configure-kb` so Hermes can
remember a default knowledge-base path through a local profile. v0.2.3 adds `bootstrap-prompt` so
users can paste a natural-language installation request into Hermes Agent.
v0.2.4 adds uploaded-file raw import and daily deterministic maintenance reports.
v0.2.5 adds `doctor` and `hermes status` for installation and pre-use diagnostics.
v0.3.0 adds `.linta/agent_access.yaml`, `agents wizard`, and Claude Desktop read-only MCP.
v0.3.1 renames the project to Linta / 灵台.
v0.3.2 adds rename migration hardening through `linta migrate`.

## Verify Installation

After init or Hermes setup, run:

```bash
linta doctor ./SimonKnowledgeBase
linta agents wizard ./SimonKnowledgeBase
linta hermes status
```

`doctor` checks the knowledge-base layout and deterministic health. `hermes status` checks installed
skills, profiles, and whether the configured knowledge-base path is valid.

## Rename Migration

After upgrading from the pre-Linta name, run:

```bash
linta migrate ./SimonKnowledgeBase --dry-run
linta migrate ./SimonKnowledgeBase
```

The migration copies legacy `.llm-wiki/agent_access.yaml` to `.linta/agent_access.yaml` when needed,
replaces legacy `llm-wiki-tags` blocks with `linta-tags`, and reports old Hermes skill directories.

## Multi-Agent Access

Use one primary read/write agent and keep other agents read-only by default:

```bash
linta agents wizard ./SimonKnowledgeBase
linta agents status ./SimonKnowledgeBase
```

The policy is stored inside the knowledge base at `.linta/agent_access.yaml`. A typical setup is
Hermes or Codex as the writer, with Claude Desktop and OpenClaw as readers. Claude Desktop defaults
to `wiki_context`, which reads confirmed/current wiki context, source cards, manifest, portfolio
pages, and indexes, but not raw sources, current drafts, human notes, or archives.

For Claude Desktop:

```bash
linta claude-desktop config ./SimonKnowledgeBase
linta claude-desktop status ./SimonKnowledgeBase
```

Add the generated MCP snippet to Claude Desktop and restart the app. The read-only boundary applies
to the Linta MCP adapter; separately granted filesystem or shell tools are outside this
project's enforcement boundary.

## Obsidian Tags and Indexes

`linta tags` writes controlled inline Markdown tags into wiki pages:

```md
<!-- linta-tags:start -->
#project/example #status/draft #capability/review
<!-- linta-tags:end -->
```

Tags are normalized to lowercase kebab-case and may use namespaces such as `#project/...`,
`#capability/...`, and `#status/...`. The CLI refuses to write tags into `ai_kb/raw/`; raw sources
remain immutable. `linta index build` writes JSON indexes under `ai_kb/wiki/indexes/` for tools.

## Uploads and Maintenance

For files uploaded through Hermes gateway or another chat surface, import the file into raw first:

```bash
linta raw import ./SimonKnowledgeBase ~/Downloads/uploaded.md --source-type docs
```

Daily maintenance should not re-ingest everything. Run:

```bash
linta maintenance daily ./SimonKnowledgeBase
```

The report identifies new raw sources, missing source cards, lint issues, and recommended actions.
LLM compilation remains the responsibility of the user's configured Agent environment, such as
Hermes.

## Safety Boundaries

- Raw files are immutable.
- `linta tags add/set` refuses to write inside `ai_kb/raw/`.
- Current state requires human confirmation.
- Export files are not the source of truth.
- Users should review diffs before committing generated changes.
- Tests must not call external LLM APIs.

## Licensing

Linta is source-available under the PolyForm Noncommercial License 1.0.0.
Noncommercial use is permitted under `LICENSE`. Commercial use requires a separate
paid commercial license; see [COMMERCIAL.md](COMMERCIAL.md).

This project is not OSI open source because commercial use is reserved.

## Hermes and Codex

Hermes integration is optional and lives under `hermes/`. It includes skills for upload import,
daily maintenance, ingest, lint, mini-kb, export, current confirmation, tags, and indexes. Codex maintenance rules live in
`AGENTS.md` and generated knowledge bases receive their own `AGENTS.md` and `ai_kb/schema/AGENTS.md`.

After installing Hermes skills, bind your default knowledge base:

```bash
linta hermes bootstrap-prompt ./SimonKnowledgeBase
linta hermes configure-kb ./SimonKnowledgeBase
```

`bootstrap-prompt` prints a natural-language prompt that Hermes Agent can follow. `configure-kb`
writes a profile under `~/.hermes/skills/linta/profiles/`.

## Examples

Example projects are scaffolded under `examples/`. The `product-knowledge-ops` example includes raw
sources, source cards, portfolio pages, current/current_draft separation, and a review-prep mini-kb.

## Roadmap

See [ROADMAP.md](ROADMAP.md).

## License

PolyForm Noncommercial License 1.0.0 for noncommercial use. Commercial use requires a separate
written agreement.
