# Obsidian Tags

llm-wiki-kit supports Obsidian-readable inline Markdown tags without making Obsidian a required
dependency.

Tags live in a managed Markdown block:

```md
<!-- llm-wiki-tags:start -->
#project/example #status/draft #capability/review
<!-- llm-wiki-tags:end -->
```

Use deterministic commands:

```bash
llm-wiki tags list ./kb/ai_kb/wiki/projects/example.md
llm-wiki tags add ./kb/ai_kb/wiki/projects/example.md --tag project/example --tag status/draft
llm-wiki tags set ./kb/ai_kb/wiki/projects/example.md --tag capability/review
llm-wiki prompt tag ./kb ai_kb/wiki/projects/example.md
```

Rules:

- Tags normalize to lowercase kebab-case.
- Namespaces such as `#project/...`, `#capability/...`, and `#status/...` are supported.
- `add` de-duplicates tags.
- `set` replaces only the managed block and leaves other page content intact.
- Writes under `ai_kb/raw/` are refused. Raw sources remain immutable.
- Tags are a reading and graph layer. They do not replace frontmatter, source cards, or the source
  manifest.

