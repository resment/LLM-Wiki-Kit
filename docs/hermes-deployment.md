# Hermes Deployment

Hermes integration is optional. Phase 4 provides bundled skill files and a deterministic installer.

Expected layout:

```text
hermes/
├─ README.md
├─ skills/
│  ├─ ingest_raw_source/
│  ├─ lint_knowledge_base/
│  ├─ generate_mini_kb/
│  ├─ export_for_ai/
│  └─ confirm_current/
└─ install_skills.sh
```

Hermes skills should follow the same safety boundaries as the CLI:

- never mutate `ai_kb/raw/`;
- write `current_draft/` by default;
- write `current/` only in an explicit confirmation skill;
- cite source paths;
- output human review questions.

## CLI Install

Dry run:

```bash
llm-wiki hermes install-skills --dry-run
```

Install to the default target:

```bash
llm-wiki hermes install-skills
```

Default target:

```text
~/.hermes/skills/llm-wiki-kit/
```

Custom target:

```bash
llm-wiki hermes install-skills --target /tmp/hermes-skills/llm-wiki-kit
```

Existing skill directories are skipped unless `--force` is provided.

## Shell Install

The repository also includes:

```bash
hermes/install_skills.sh /tmp/hermes-skills/llm-wiki-kit
```

The shell script is intentionally conservative: it creates the target directory and skips existing
skill directories.
