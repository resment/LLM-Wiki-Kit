# Claude Desktop Read-Only MCP

v0.3.0 adds a read-only Claude Desktop adapter through MCP. Claude Desktop uses its own LLM
configuration; llm-wiki-kit only exposes deterministic read tools.

## Configure Agent Access

Create an access policy inside the knowledge base:

```bash
llm-wiki agents wizard /path/to/YourKnowledgeBase
```

Choose the primary read/write agent when prompted. A common setup is Hermes as the writer and Claude
Desktop as a reader:

```bash
llm-wiki agents configure /path/to/YourKnowledgeBase --primary-agent hermes
```

The policy is written to:

```text
/path/to/YourKnowledgeBase/.llm-wiki/agent_access.yaml
```

Claude Desktop defaults to `mode: read` and `read_scope: wiki_context`.

## Claude Desktop Config

Print the JSON snippet:

```bash
llm-wiki claude-desktop config /path/to/YourKnowledgeBase
```

Add the snippet to Claude Desktop's MCP config. On macOS, open Claude Desktop Settings, go to
Developer, and use Edit Config. Restart Claude Desktop after saving.

The generated server uses:

```bash
llm-wiki mcp serve --agent claude-desktop --kb-root /path/to/YourKnowledgeBase
```

## Read Scope

The default `wiki_context` scope allows Claude Desktop to read current wiki context, source cards,
manifest, portfolio pages, and generated indexes. It does not allow reads from `ai_kb/raw/`,
`ai_kb/wiki/current_draft/`, `human/`, or `archive/`.

Use a narrower scope for export-only consumption:

```bash
llm-wiki agents set /path/to/YourKnowledgeBase \
  --agent claude-desktop \
  --mode read \
  --read-scope exports-only
```

Use `full-kb` only when Claude Desktop should be able to read raw sources as well.

## Status Checks

```bash
llm-wiki agents status /path/to/YourKnowledgeBase
llm-wiki claude-desktop status /path/to/YourKnowledgeBase
llm-wiki doctor /path/to/YourKnowledgeBase
```

## Boundary

The read-only guarantee applies to the llm-wiki-kit MCP adapter. If Claude Desktop is separately
given a filesystem or shell MCP server with write access to the same directory, that external server
is outside llm-wiki-kit's enforcement boundary.
