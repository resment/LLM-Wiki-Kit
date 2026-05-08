# Claude Desktop Read-Only MCP

v0.3.0 adds a read-only Claude Desktop adapter through MCP. Claude Desktop uses its own LLM
configuration; Linta only exposes deterministic read tools.

v0.3.3 adds practical context tools so Claude Desktop can discover, search, read, and bundle
compiled Linta context inside a Claude Project without reading raw source material.

## Configure Agent Access

Create an access policy inside the knowledge base:

```bash
linta agents wizard /path/to/YourKnowledgeBase
```

Choose the primary read/write agent when prompted. A common setup is Hermes as the writer and Claude
Desktop as a reader:

```bash
linta agents configure /path/to/YourKnowledgeBase --primary-agent hermes
```

The policy is written to:

```text
/path/to/YourKnowledgeBase/.linta/agent_access.yaml
```

Claude Desktop defaults to `mode: read` and `read_scope: wiki_context`.

## Claude Desktop Config

Print the JSON snippet:

```bash
linta claude-desktop config /path/to/YourKnowledgeBase
```

Add the snippet to Claude Desktop's MCP config. On macOS, open Claude Desktop Settings, go to
Developer, and use Edit Config. Restart Claude Desktop after saving.

The generated server uses:

```bash
linta mcp serve --agent claude-desktop --kb-root /path/to/YourKnowledgeBase
```

## Read Scope

The default `wiki_context` scope allows Claude Desktop to read current wiki context, source cards,
manifest, portfolio pages, and generated indexes. It does not allow reads from `ai_kb/raw/`,
`ai_kb/wiki/current_draft/`, `human/`, or `archive/`.

Use a narrower scope for export-only consumption:

```bash
linta agents set /path/to/YourKnowledgeBase \
  --agent claude-desktop \
  --mode read \
  --read-scope exports-only
```

Use `full-kb` only for lower-level MCP tools when Claude Desktop should be able to read raw sources
as well. The practical context tools still exclude raw sources so Claude Project work stays on the
compiled wiki layer.

## Claude Project Workflow

In a Claude Project, ask Claude to use the Linta MCP tools in this order:

```text
Use the Linta MCP server. Start with context_overview, then use context_search,
context_read, and context_bundle to decide which compiled wiki context is relevant.
Do not ask for raw sources.
```

The practical tools are:

- `context_overview`: shows available compiled context entrypoints and the read boundary.
- `context_search`: searches allowed compiled context and returns paths, lines, and snippets.
- `context_read`: reads one allowed context file.
- `context_bundle`: builds a compact package from a query or explicit paths.

## Status Checks

```bash
linta agents status /path/to/YourKnowledgeBase
linta claude-desktop status /path/to/YourKnowledgeBase
linta doctor /path/to/YourKnowledgeBase
```

## Boundary

The read-only guarantee applies to the Linta MCP adapter. If Claude Desktop is separately
given a filesystem or shell MCP server with write access to the same directory, that external server
is outside Linta's enforcement boundary.
