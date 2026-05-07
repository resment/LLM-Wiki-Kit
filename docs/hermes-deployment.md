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
│  ├─ import_uploaded_raw_source/
│  ├─ daily_maintenance/
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
existing deterministic CLI workflows: `linta tags list/add/set`, `linta prompt tag`, and
`linta index build`.

## CLI Install

Dry run:

```bash
linta hermes install-skills --dry-run
```

Install to the default target:

```bash
linta hermes install-skills
linta hermes status
```

Bind the default knowledge base for first-use Hermes workflows:

```bash
linta agents wizard /path/to/YourKnowledgeBase
linta hermes bootstrap-prompt /path/to/YourKnowledgeBase
linta hermes configure-kb /path/to/YourKnowledgeBase
```

`bootstrap-prompt` prints a natural-language request that can be pasted into Hermes Agent. The
agent can then run the deterministic install and profile commands for the user.

Default target:

```text
~/.hermes/skills/linta/
```

Custom target:

```bash
linta hermes install-skills --target /tmp/hermes-skills/linta
```

Existing skill directories are skipped unless `--force` is provided.

Check installed skills and profiles:

```bash
linta hermes status
linta hermes status --target /tmp/hermes-skills/linta
```

## Knowledge Base Profiles

v0.3.0 adds KB-local Agent access policy:

```bash
linta agents configure /path/to/YourKnowledgeBase --primary-agent hermes
linta agents status /path/to/YourKnowledgeBase
```

Hermes profiles now include the current Hermes access mode when `.linta/agent_access.yaml`
exists. A common setup is Hermes as the read/write Agent and Claude Desktop, Codex, or OpenClaw as
read-only consumers.

`configure-kb` writes a profile file under:

```text
~/.hermes/skills/linta/profiles/default.md
```

Use `--profile <name>` for multiple knowledge bases and `--target <dir>` when skills are installed
outside the default Hermes directory. Existing profiles are not overwritten unless `--force` is
provided.

## Natural-Language Agent Install

Generate the prompt:

```bash
linta hermes bootstrap-prompt /path/to/YourKnowledgeBase
```

Paste the output into Hermes Agent. The prompt instructs Hermes to install skills, configure the
default profile, run lint, and report what changed.

## Uploaded File Workflow

When a user uploads a file through Hermes gateway, first import it into raw:

```bash
linta raw import /path/to/YourKnowledgeBase /path/to/uploaded.md --source-type docs
```

Then create a source card and ingest only that imported raw source. Do not run a full re-ingest.

## Daily Maintenance

Daily maintenance is deterministic:

```bash
linta maintenance daily /path/to/YourKnowledgeBase
```

The report identifies new raw sources, missing source cards, lint findings, and recommended actions.
Use Hermes' already configured LLM environment only when the report recommends a targeted ingest or
semantic wiki update.

## Natural-Language Examples

- "Use Linta default knowledge base and process the file I just uploaded."
- "Run daily maintenance for my default Linta knowledge base."
- "Check whether Linta Hermes skills are installed and which KB profile is active."
- "Configure Hermes as the primary linta writer and keep Claude Desktop read-only."

## Shell Install

The repository also includes:

```bash
hermes/install_skills.sh /tmp/hermes-skills/linta
```

The shell script is intentionally conservative: it creates the target directory and skips existing
skill directories.
