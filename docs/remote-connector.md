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

Set private OAuth values outside the repository:

```bash
export LINTA_REMOTE_MCP_PUBLIC_BASE_URL="https://your-linta.example.com"
export LINTA_OAUTH_CLIENT_ID="replace-with-client-id"
export LINTA_OAUTH_CLIENT_SECRET="replace-with-client-secret"
export LINTA_OAUTH_APPROVAL_TOKEN="replace-with-private-approval-token"
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

Claude custom connectors use OAuth. Configure Claude with:

```text
Name: Linta
Remote MCP server URL: https://your-linta.example.com/mcp
OAuth Client ID: replace-with-client-id
OAuth Client Secret: replace-with-client-secret
```

When Claude opens the Linta authorization page, enter the private value from
`LINTA_OAUTH_APPROVAL_TOKEN`. Linta then issues an OAuth bearer token to Claude. Tokens are stored
in memory; after restarting `linta mcp serve-http`, reconnect the Claude connector.

The server also supports a direct bearer token for non-Claude clients that can send custom headers:

```bash
export LINTA_REMOTE_MCP_TOKEN="replace-with-private-bearer-token"
```

Claude's custom connector form does not provide a generic `Authorization` header field, so use the
OAuth settings for Claude.

## Claude Setup

In Claude, add a custom connector with the public HTTPS URL:

```text
https://your-linta.example.com/mcp
```

Fill the advanced OAuth Client ID and OAuth Client Secret fields with the values from your private
environment. Mobile clients can use connectors already added through Claude Desktop or claude.ai,
but cannot add new custom servers directly.

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
