# Manage Obsidian Tags

Use llm-wiki-kit deterministic tag commands for Obsidian-readable Markdown tags.

Commands:

```bash
llm-wiki tags list <md_path>
llm-wiki tags add <md_path> --tag project/example --tag status/draft
llm-wiki tags set <md_path> --tag project/example --tag capability/review
llm-wiki prompt tag <kb_root> <md_path>
```

Rules:

- Do not modify `ai_kb/raw/`.
- Use the managed `llm-wiki-tags` block.
- Normalize tags to lowercase kebab-case.
- Prefer namespaces: `#project/...`, `#domain/...`, `#capability/...`, `#concept/...`, `#status/...`, `#type/...`.
- Run `llm-wiki lint <kb_root>` after writes when practical.

Output changed files, recommended tags, and human review notes.
