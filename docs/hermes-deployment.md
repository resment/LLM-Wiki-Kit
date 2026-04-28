# Hermes Deployment

Hermes integration is optional. The repository provides bundled skill files and a deterministic installer.

Expected layout:

```text
hermes/
├─ README.md
├─ skills/
│  ├─ ingest_raw_source/
│  ├─ lint_knowledge_base/
│  ├─ manage_obsidian_tags/
│  ├─ build_indexes/
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

v0.2.1 adds Hermes skills for Obsidian tags and machine-readable indexes. These skills wrap the
existing deterministic CLI workflows: `llm-wiki tags list/add/set`, `llm-wiki prompt tag`, and
`llm-wiki index build`.

## CLI Install

Dry run:

```bash
llm-wiki hermes install-skills --dry-run
```

Install to the default target:

```bash
llm-wiki hermes install-skills
```

Bind the default knowledge base for first-use Hermes workflows:

```bash
llm-wiki hermes bootstrap-prompt /path/to/YourKnowledgeBase
llm-wiki hermes configure-kb /path/to/YourKnowledgeBase
```

`bootstrap-prompt` prints a natural-language request that can be pasted into Hermes Agent. The
agent can then run the deterministic install and profile commands for the user.

Default target:

```text
~/.hermes/skills/llm-wiki-kit/
```

Custom target:

```bash
llm-wiki hermes install-skills --target /tmp/hermes-skills/llm-wiki-kit
```

Existing skill directories are skipped unless `--force` is provided.

## Knowledge Base Profiles

`configure-kb` writes a profile file under:

```text
~/.hermes/skills/llm-wiki-kit/profiles/default.md
```

Use `--profile <name>` for multiple knowledge bases and `--target <dir>` when skills are installed
outside the default Hermes directory. Existing profiles are not overwritten unless `--force` is
provided.

## Natural-Language Agent Install

Generate the prompt:

```bash
llm-wiki hermes bootstrap-prompt /path/to/YourKnowledgeBase
```

Paste the output into Hermes Agent. The prompt instructs Hermes to install skills, configure the
default profile, run lint, and report what changed.

## Shell Install

The repository also includes:

```bash
hermes/install_skills.sh /tmp/hermes-skills/llm-wiki-kit
```

The shell script is intentionally conservative: it creates the target directory and skips existing
skill directories.
