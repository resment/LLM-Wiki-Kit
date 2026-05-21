# Linta Remote Claude Connector

Linta can run as a remote MCP HTTP endpoint for Claude custom connectors. This is separate from
Claude Desktop's local `stdio` MCP configuration.

## Runtime Shape

```text
Claude App / Claude Desktop web connector / Claude mobile
        |
        | HTTPS remote MCP connector
        v
Reverse proxy or tunnel
        |
        v
linta mcp serve-http
        |
        v
Linta knowledge base
```

The service must be reachable by Claude over the public internet. Keep the Linta process bound to
`127.0.0.1` unless your deployment environment requires a different private bind address, then put
HTTPS and access controls in front of it.

## Start the Endpoint

Set a private bearer token outside the repository:

```bash
export LINTA_REMOTE_MCP_TOKEN="replace-with-a-private-token"
linta mcp serve-http \
  --kb-root /path/to/YourKnowledgeBase \
  --host 127.0.0.1 \
  --port 8765
```

The MCP endpoint is:

```text
http://127.0.0.1:8765/mcp
```

Expose it through HTTPS before adding it to Claude:

```text
https://your-linta.example.com/mcp
```

Do not commit the real URL, IP address, bearer token, reverse proxy config with private hostnames,
or personal knowledge-base path.

## Auth Boundary

Every `POST /mcp` request must include:

```http
Authorization: Bearer <token>
```

The token value is read from `LINTA_REMOTE_MCP_TOKEN` by default. You can choose another variable:

```bash
linta mcp serve-http --kb-root /path/to/YourKnowledgeBase --token-env MY_PRIVATE_TOKEN
```

## Claude Setup

In Claude, add a custom connector with the public HTTPS URL:

```text
https://your-linta.example.com/mcp
```

If your Claude plan or organization flow requires OAuth instead of a static connector credential,
add an OAuth layer in front of the Linta service. Keep the token between that auth layer and Linta
private.

## Read Tools

Remote MCP uses the same practical context tools as the local Claude Desktop adapter:

- `context_overview`
- `context_search`
- `context_read`
- `context_bundle`

These tools read compiled wiki context and do not read `ai_kb/raw/`.

## Write Tools

Write tools are exposed only when the configured agent has write mode:

```bash
linta agents set /path/to/YourKnowledgeBase \
  --agent claude-desktop \
  --mode write \
  --read-scope wiki-context
```

The built-in write tools are intentionally limited:

- `write_current_draft`: writes one Markdown file under `ai_kb/wiki/current_draft/`.
- `propose_wiki_patch`: stores a patch proposal under `ai_kb/wiki/current_draft/patches/`.

They do not edit `ai_kb/raw/`, `human/`, `archive/`, or confirmed `ai_kb/wiki/current/` pages.

## Health Check

The endpoint exposes a basic unauthenticated health check:

```text
GET /health
```

It returns package and agent metadata only. It does not return knowledge-base content or secrets.
