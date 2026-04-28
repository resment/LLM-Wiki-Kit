# Obsidian Tagging Prompt

You are suggesting Obsidian inline tags for an LLM Wiki Markdown file.

Knowledge base root:
- {{kb_root}}

Read and obey:
- {{agents_path}}

Target Markdown file:
- {{markdown_path}}

Rules:
1. Do not modify, move, rename, or delete anything under `ai_kb/raw/`.
2. If the target file is under `ai_kb/raw/`, only suggest tags; do not edit the file.
3. Prefer tags derived from existing structured fields: projects, domains, capabilities, concepts,
   status, and source type.
4. Use Obsidian inline tags, not YAML tags.
5. Use lowercase kebab-case.
6. Use namespaces when useful:
   - `#project/...`
   - `#domain/...`
   - `#capability/...`
   - `#concept/...`
   - `#status/...`
   - `#type/...`
7. Keep tags broad enough to be reusable in Obsidian.
8. If uncertain, output `proposed_tags` separately instead of inventing precise tags.

Output:
- recommended_tags
- proposed_tags
- reasoning
- source paths checked
