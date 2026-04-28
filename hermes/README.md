# Hermes Adapter

This directory contains optional Hermes skills for maintaining an llm-wiki-kit knowledge base.

The skills are prompt-and-procedure adapters. They do not call external APIs by themselves and they
follow the same safety model as the CLI:

- never mutate `ai_kb/raw/`;
- write `current_draft/` by default;
- write `current/` only through the explicit confirmation workflow;
- preserve source paths;
- output human review questions.

Bundled skills:

- `ingest_raw_source`
- `lint_knowledge_base`
- `manage_obsidian_tags`
- `build_indexes`
- `generate_mini_kb`
- `export_for_ai`
- `confirm_current`

## Install

Dry run:

```bash
llm-wiki hermes install-skills --dry-run
```

Default target:

```text
~/.hermes/skills/llm-wiki-kit/
```

Custom target:

```bash
llm-wiki hermes install-skills --target /path/to/hermes/skills/llm-wiki-kit
```

Existing skill directories are skipped unless `--force` is provided.

## Configure a Knowledge Base

After installing skills, bind the default knowledge base:

```bash
llm-wiki hermes bootstrap-prompt /path/to/YourKnowledgeBase
llm-wiki hermes configure-kb /path/to/YourKnowledgeBase
```

`bootstrap-prompt` prints a natural-language installation request that can be pasted into Hermes
Agent.

This writes:

```text
~/.hermes/skills/llm-wiki-kit/profiles/default.md
```

Use `--profile <name>` for additional knowledge bases.
