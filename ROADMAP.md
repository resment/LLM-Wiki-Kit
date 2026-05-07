# Roadmap

## v0.3.2 Status

Implemented:

- `linta migrate <kb_root>` for safe rename-era migration.
- Dry-run and JSON migration report output.
- Legacy `.llm-wiki/agent_access.yaml` copy to `.linta/agent_access.yaml`.
- Legacy `llm-wiki-tags` block replacement with `linta-tags`.
- Doctor warning for legacy access-policy paths.

## v0.3.1 Status

Implemented:

- Renamed the public project to `Linta` / `灵台`.
- Added the primary `linta` CLI and kept `llm-wiki` as a deprecated alias.
- Renamed the Python import package to `linta`.
- Moved new Agent access policy path to `.linta/agent_access.yaml` with legacy read fallback.

## v0.3.0 Status

Implemented:

- `.linta/agent_access.yaml` for per-knowledge-base Agent access policy.
- `linta agents wizard/status/configure/set/policy` for read/write Agent setup.
- Claude Desktop read-only MCP adapter through `linta mcp serve`.
- `linta claude-desktop config/status` for first-use setup and verification.

## v0.2.5 Status

Implemented:

- `linta doctor` for read-only knowledge-base diagnostics.
- `linta hermes status` for installed skill and profile validation.
- Installation verification docs for CLI and Hermes setup.

## v0.2.4 Status

Implemented:

- `linta raw import` for deterministic uploaded-file import into `ai_kb/raw/`.
- `linta maintenance daily` for deterministic daily reports without full re-ingest.
- Hermes `import_uploaded_raw_source` and `daily_maintenance` skills.

## v0.2.3 Status

Implemented:

- `linta hermes bootstrap-prompt <kb_root>` for natural-language Hermes Agent installation.
- First-use prompt text covering skill install, profile binding, lint verification, and safety rules.

## v0.2.2 Status

Implemented:

- `linta hermes configure-kb <kb_root>` for first-use Hermes knowledge-base binding.
- Local Hermes profiles under `~/.hermes/skills/linta/profiles/`.
- Install guidance that points users to configure a default knowledge-base path.

## v0.2.1 Status

Implemented:

- Hermes `manage_obsidian_tags` skill for v0.2 tag workflows.
- Hermes `build_indexes` skill for deterministic JSON index generation.
- Documentation and package assets for Hermes tags/index workflows.

## v0.2 Status

Implemented:

- Obsidian-friendly managed Markdown tag blocks with `linta tags list/add/set`.
- External tag suggestion prompt via `linta prompt tag`.
- Manifest scan preserves manually maintained fields by default.
- Machine-readable indexes under `ai_kb/wiki/indexes/`.
- Stronger lint checks for Markdown links, source cards, current citations, and managed tags.

## v0.1 Status

Implemented:

- Phase 1: project scaffold and `linta init`.
- Phase 2: deterministic manifest, source-card, prompt, lint, export, and mini-kb tools.
- Phase 3: richer docs, templates, and anonymized product knowledge operations example.
- Phase 4: optional Hermes adapter skills and installer.
- Phase 5: release polish, packaging metadata, and example validation.

## Licensing

Linta is source-available under PolyForm Noncommercial License 1.0.0 for noncommercial use.
Commercial use requires a separate written commercial license.

## Next Candidates

- Add release publishing docs and automation.
- Add more example knowledge-base shapes outside product knowledge operations.
- Add optional richer Obsidian graph conventions without requiring an Obsidian plugin.
- Add source-card/current consistency reports beyond lint output.
- Package Claude Desktop as a Desktop Extension after MCP dogfooding.

## Non-Goals for v0.1

- No built-in LLM API calls.
- No vector database.
- No Web UI.
- No Obsidian plugin.
- No OS-level permission model.
