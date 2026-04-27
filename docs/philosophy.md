# Philosophy

llm-wiki-kit treats knowledge bases as a small compile pipeline:

1. Raw sources are immutable evidence.
2. Source cards summarize and classify evidence without replacing it.
3. Wiki pages organize knowledge across projects, domains, capabilities, and concepts.
4. `current_draft/` contains AI-maintained proposed current state.
5. `current/` contains human-confirmed current state.
6. `export_for_ai/` contains compact context for external AI tools.

The framework deliberately avoids hidden inference. Important claims should cite source paths,
and conflicts should remain visible until a human resolves them.

This is different from ordinary RAG. RAG retrieves chunks at query time. llm-wiki-kit encourages
agents to maintain a reviewed Markdown knowledge layer over time, so later queries start from a
stable, auditable current-state view instead of re-reading every raw document.
