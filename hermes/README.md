# Hermes Adapter

This directory contains optional Hermes skills for maintaining an llm-wiki-kit knowledge base.

The skills are prompt-and-procedure adapters. They do not call external APIs by themselves and they
follow the same safety model as the CLI:

- never mutate `ai_kb/raw/`;
- write `current_draft/` by default;
- write `current/` only through the explicit confirmation workflow;
- preserve source paths;
- output human review questions.

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
