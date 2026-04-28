# Roadmap

## v0.2 Status

Implemented:

- Obsidian-friendly managed Markdown tag blocks with `llm-wiki tags list/add/set`.
- External tag suggestion prompt via `llm-wiki prompt tag`.
- Manifest scan preserves manually maintained fields by default.
- Machine-readable indexes under `ai_kb/wiki/indexes/`.
- Stronger lint checks for Markdown links, source cards, current citations, and managed tags.

## v0.1 Status

Implemented:

- Phase 1: project scaffold and `llm-wiki init`.
- Phase 2: deterministic manifest, source-card, prompt, lint, export, and mini-kb tools.
- Phase 3: richer docs, templates, and anonymized product knowledge operations example.
- Phase 4: optional Hermes adapter skills and installer.
- Phase 5: release polish, packaging metadata, and example validation.

## Licensing

llm-wiki-kit is source-available under PolyForm Noncommercial License 1.0.0 for noncommercial use.
Commercial use requires a separate written commercial license.

## Next Candidates

- Add release publishing docs and automation.
- Add more example knowledge-base shapes outside product knowledge operations.
- Add optional richer Obsidian graph conventions without requiring an Obsidian plugin.
- Add source-card/current consistency reports beyond lint output.

## Non-Goals for v0.1

- No built-in LLM API calls.
- No vector database.
- No Web UI.
- No Obsidian plugin.
- No multi-user permission model.
