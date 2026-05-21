# Linta（灵台）

`Linta`（中文名：灵台） helps you turn scattered notes, meeting transcripts, documents, and AI
conversations into a knowledge base that future AI assistants can actually understand.

Chinese README: [README_CN.md](README_CN.md)

Most personal or team knowledge bases become hard for AI to use: raw files pile up, people and
project names drift, old context gets mixed with current truth, and every new chat starts from
scratch. Linta gives your AI tools a clean, reviewable memory layer built from Markdown files,
source citations, and explicit human review.

## Why Linta

- Keep the original material untouched, so meeting notes and documents stay trustworthy.
- Let AI compile messy material into clean wiki pages, source cards, project maps, and current-state
  summaries.
- Give ChatGPT, Claude, Gemini, Hermes, Codex, and similar tools a compact context layer instead of
  dumping raw folders into every conversation.
- Track people, teams, aliases, product lines, and project relationships so the model can tell who
  is related to what.
- Keep historical context separate from current truth, so old roles and decisions do not overwrite
  today’s situation.

## Install, Upgrade, Remove

For most users, Linta is just a small command-line helper. Install it once, then use it from Codex,
Hermes, Terminal, or any agent that can run local commands.

| Goal | Command | What happens |
| --- | --- | --- |
| Install Linta | `pip install "linta @ git+https://github.com/resment/Linta.git"` | Adds the `linta` command to your Python environment. |
| Upgrade to the latest version | `pip install --upgrade "linta @ git+https://github.com/resment/Linta.git"` | Replaces the installed command with the newest release from GitHub. |
| Check the installed version | `linta --version` | Prints the current Linta version. |
| Remove Linta | `pip uninstall linta` | Removes the Python package and command. Your knowledge-base folders stay on disk. |
| Work on the source code | `pip install -e ".[dev]"` | Installs a cloned checkout in editable development mode. |

If your Python installation blocks global package installs, create a virtual environment first or
install Linta inside the same environment used by your agent tool.

## What You Can Ask

These are natural-language requests you can give to Codex, Hermes, or another agent working inside
a Linta knowledge base. The matching command is shown for users who want to run it directly.

| Say this | Command behind it | What it does |
| --- | --- | --- |
| "Create a new AI-readable knowledge base here." | `linta init ./MyKnowledgeBase` | Creates the standard folders and starter rules. |
| "Import this uploaded document into the knowledge base." | `linta raw import ./MyKnowledgeBase ~/Downloads/file.md --source-type docs` | Copies a file into immutable raw material. |
| "Prepare this meeting note for AI ingestion." | `linta source-card create ./MyKnowledgeBase ai_kb/raw/meetings/example.md` | Creates a structured source card for one raw file. |
| "Ingest this source and update the related wiki pages." | `linta prompt ingest ./MyKnowledgeBase ai_kb/raw/meetings/example.md` | Gives the agent the exact update workflow. |
| "Extract people, teams, aliases, and project relationships from this source." | `linta prompt entities ./MyKnowledgeBase ai_kb/raw/meetings/example.md` | Focuses the agent on entity and project-map updates. |
| "Build a small context pack for this project review." | `linta mini-kb create ./MyKnowledgeBase --topic "Project" --purpose "Review prep"` | Creates a compact mini knowledge base for one task. |
| "Check whether my knowledge base is healthy." | `linta doctor ./MyKnowledgeBase` | Checks layout, required files, and setup health. |
| "What changed recently and what needs maintenance?" | `linta maintenance daily ./MyKnowledgeBase` | Finds new raw sources, missing source cards, and lint issues. |
| "Make this knowledge base readable by Claude Desktop." | `linta claude-desktop config ./MyKnowledgeBase` | Prints the local read-only MCP config snippet. |
| "Serve this knowledge base as a remote Claude connector." | `linta mcp serve-http --kb-root ./MyKnowledgeBase` | Starts a token-protected remote MCP endpoint. |
| "Export confirmed current knowledge for other AI tools." | `linta export current ./MyKnowledgeBase` | Copies reviewed current pages into the export layer. |

## Quick Start

```bash
pip install "linta @ git+https://github.com/resment/Linta.git"
linta init ./MyKnowledgeBase
```

Then put files under `ai_kb/raw/`, ask an agent to ingest them with `linta prompt ingest`, review
the generated wiki updates, and export confirmed context when another AI tool needs it.

For local development after cloning this repository, use `pip install -e ".[dev]"`.

## Current Release

v0.3.7 adds a token-protected remote MCP HTTP endpoint for Claude custom connectors, plus
policy-gated draft and patch proposal tools. It also keeps the v0.3 line features: deterministic
scaffolding, manifest scanning, source-card templates, prompt rendering, linting, current export,
mini-kb draft generation, optional Hermes skills, Obsidian-friendly Markdown tags,
machine-readable indexes, doctor diagnostics, multi-agent access profiles, entity context, and
Claude Desktop MCP practical context tools.

Linta does not call an LLM API by default. It gives your chosen agent a safe structure and prompts;
the source-backed semantic writing happens in your agent environment.

## Core Layout

```text
human/                 Personal writing area. AI should not edit it by default.
ai_kb/raw/             Immutable source of truth.
ai_kb/wiki/            AI-compiled knowledge layer.
ai_kb/wiki/entities/   People, team, product-line, alias, and relationship context.
ai_kb/wiki/indexes/    Machine-readable JSON indexes.
ai_kb/schema/          Maintenance rules for agents.
ai_kb/export_for_ai/   Consumption layer for other AI tools.
archive/               Archived material.
```

## Current State

`current_draft/` is AI-generated and needs review. `current/` is the human-confirmed current state. Agents may update drafts, but must not update `current/` unless the user explicitly confirms.

## Command Reference

v0.3.6 supports:

```bash
linta init ./MyKnowledgeBase
linta manifest scan ./MyKnowledgeBase
linta manifest scan ./MyKnowledgeBase --no-preserve-manual-fields
linta source-card create ./MyKnowledgeBase ai_kb/raw/meetings/example.md
linta prompt ingest ./MyKnowledgeBase ai_kb/raw/meetings/example.md
linta prompt entities ./MyKnowledgeBase ai_kb/raw/meetings/example.md
linta prompt tag ./MyKnowledgeBase ai_kb/wiki/projects/example.md
linta tags list ./MyKnowledgeBase/ai_kb/wiki/projects/example.md
linta tags add ./MyKnowledgeBase/ai_kb/wiki/projects/example.md --tag project/example
linta tags set ./MyKnowledgeBase/ai_kb/wiki/projects/example.md --tag status/draft
linta index build ./MyKnowledgeBase
linta raw import ./MyKnowledgeBase ~/Downloads/uploaded.md --source-type docs
linta maintenance daily ./MyKnowledgeBase
linta doctor ./MyKnowledgeBase
linta migrate ./MyKnowledgeBase --dry-run
linta agents wizard ./MyKnowledgeBase
linta agents status ./MyKnowledgeBase
linta claude-desktop config ./MyKnowledgeBase
linta claude-desktop status ./MyKnowledgeBase
linta claude-desktop project-instructions ./MyKnowledgeBase
linta mcp serve --agent claude-desktop --kb-root ./MyKnowledgeBase
linta mcp serve-http --kb-root ./MyKnowledgeBase --host 127.0.0.1 --port 8765
linta prompt lint-ai ./MyKnowledgeBase
linta lint ./MyKnowledgeBase
linta export current ./MyKnowledgeBase
linta mini-kb create ./MyKnowledgeBase --topic "Example" --purpose "Review prep"
linta hermes install-skills --dry-run
linta hermes status
linta hermes bootstrap-prompt ./MyKnowledgeBase
linta hermes configure-kb ./MyKnowledgeBase
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
v0.3.3 adds practical Claude Desktop MCP context tools for overview, search, read, and bundle.
v0.3.4 adds Claude Project instructions for practical Linta MCP usage.
v0.3.5 adds context freshness signals for Claude Desktop MCP overview and bundles.
v0.3.6 adds entity context, focused entity prompts, and entity relationship indexes.
v0.3.7 adds token-protected remote MCP serving for Claude custom connectors and safe draft/patch
write tools.

## Verify Installation

After init or Hermes setup, run:

```bash
linta doctor ./MyKnowledgeBase
linta agents wizard ./MyKnowledgeBase
linta hermes status
```

`doctor` checks the knowledge-base layout and deterministic health. `hermes status` checks installed
skills, profiles, and whether the configured knowledge-base path is valid.

## Rename Migration

After upgrading from the pre-Linta name, run:

```bash
linta migrate ./MyKnowledgeBase --dry-run
linta migrate ./MyKnowledgeBase
```

The migration copies legacy `.llm-wiki/agent_access.yaml` to `.linta/agent_access.yaml` when needed,
replaces legacy `llm-wiki-tags` blocks with `linta-tags`, and reports old Hermes skill directories.

## Multi-Agent Access

Use one primary read/write agent and keep other agents read-only by default:

```bash
linta agents wizard ./MyKnowledgeBase
linta agents status ./MyKnowledgeBase
```

The policy is stored inside the knowledge base at `.linta/agent_access.yaml`. A typical setup is
Hermes or Codex as the writer, with Claude Desktop and OpenClaw as readers. Claude Desktop defaults
to `wiki_context`, which reads confirmed/current wiki context, source cards, manifest, portfolio
pages, and indexes, but not raw sources, current drafts, human notes, or archives.

For Claude Desktop:

```bash
linta claude-desktop config ./MyKnowledgeBase
linta claude-desktop status ./MyKnowledgeBase
linta claude-desktop project-instructions ./MyKnowledgeBase
```

Add the generated MCP snippet to Claude Desktop and restart the app. The read-only boundary applies
to the Linta MCP adapter; separately granted filesystem or shell tools are outside this
project's enforcement boundary.

Claude Desktop should start with the `context_overview` MCP tool, then use `context_search`,
`context_read`, and `context_bundle` to choose relevant compiled wiki context. These practical
context tools do not read `ai_kb/raw/`; raw remains the source-material layer for the primary
writer agent.

Paste the `project-instructions` output into Claude Project instructions so Claude starts with
Linta context tools, cites Linta paths, and reports missing compiled context instead of requesting
raw sources.

`context_overview` and `context_bundle` include freshness signals for missing indexes, missing
current context, missing source cards, manifest inconsistency, stale current pages, and lint errors.
If warnings are present, Claude should ask the primary writer Agent to run `linta maintenance daily`
before relying on the context.

## Remote Claude Connector

Claude App, Claude Desktop web connectors, and Claude mobile use remote MCP connectors through
Anthropic's cloud infrastructure. They cannot use a private local `stdio` server unless you are
using Claude Desktop's local config mechanism. To make Linta available from anywhere, deploy the
HTTP MCP endpoint somewhere Claude can reach:

```bash
export LINTA_REMOTE_MCP_TOKEN="replace-with-a-private-token"
linta mcp serve-http --kb-root ./MyKnowledgeBase --host 127.0.0.1 --port 8765
```

Put a reverse proxy or tunnel with HTTPS in front of that local process, then add only the public
endpoint to Claude as a custom connector:

```text
https://your-linta.example.com/mcp
```

Do not commit real domains, IP addresses, tokens, client secrets, or personal knowledge-base paths.
Use `.env` or your deployment secret store for `LINTA_REMOTE_MCP_TOKEN`.

Remote write tools are exposed only when the configured agent has `mode: write` in
`.linta/agent_access.yaml`. The built-in write tools are intentionally narrow:

- `write_current_draft` writes Markdown only under `ai_kb/wiki/current_draft/`.
- `propose_wiki_patch` stores a reviewable patch note under `ai_kb/wiki/current_draft/patches/`.

They do not edit `ai_kb/raw/`, `human/`, or `archive/`, and they do not promote drafts into
`ai_kb/wiki/current/`.

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

## Entity Context

Entity context lives under `ai_kb/wiki/entities/` and `ai_kb/wiki/portfolio/project_map.md`. Use it
to maintain stable IDs, aliases, people, teams, product lines, project mappings, and time-sliced
relationships. Relationship entries should carry fields such as `effective_from`, `effective_to`,
`relationship_type`, `target_entity`, and `source_path` so historical sources keep their original
organizational context.

Use `linta prompt entities <kb_root> <raw_source>` to generate an agent prompt for focused entity
updates. Entity pages should avoid conclusion-style personal judgments and should instead record
source-backed behavior patterns, concerns, decision scope, communication patterns, and historical
cases. `linta index build` emits `entities.json`, `relationships.json`, and `project_map.json` in
addition to the existing source, project, capability, and tag indexes.

## Uploads and Maintenance

For files uploaded through Hermes gateway or another chat surface, import the file into raw first:

```bash
linta raw import ./MyKnowledgeBase ~/Downloads/uploaded.md --source-type docs
```

Daily maintenance should not re-ingest everything. Run:

```bash
linta maintenance daily ./MyKnowledgeBase
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
linta hermes bootstrap-prompt ./MyKnowledgeBase
linta hermes configure-kb ./MyKnowledgeBase
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
