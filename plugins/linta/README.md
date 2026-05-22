# Linta Codex Plugin

This plugin teaches Codex how to work inside Linta Markdown knowledge bases.

It provides a `linta` skill for repository and knowledge-base maintenance tasks:

- initialize a standard Linta knowledge base
- import raw source files without mutating `ai_kb/raw/`
- create source cards and render ingest/entity/lint prompts
- build indexes, run lint checks, and export confirmed current context
- keep generated output deterministic and source-backed

The plugin does not store credentials, private domains, IP addresses, or personal knowledge-base paths. Use local Codex configuration, `.env`, or deployment secrets for private values.
