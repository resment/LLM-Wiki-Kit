"""Remote HTTP transport for the Linta MCP server."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from linta import __version__
from linta.mcp_server import ReadOnlyMcpServer

DEFAULT_REMOTE_TOKEN_ENV = "LINTA_REMOTE_MCP_TOKEN"


@dataclass(frozen=True)
class RemoteMcpConfig:
    kb_root: Path
    agent: str
    host: str
    port: int
    token: str
    path: str = "/mcp"


class RemoteMcpError(Exception):
    """Remote MCP configuration error."""


def token_from_env(env_name: str = DEFAULT_REMOTE_TOKEN_ENV) -> str:
    token = os.environ.get(env_name, "").strip()
    if not token:
        raise RemoteMcpError(f"Missing bearer token. Set {env_name}.")
    return token


def serve_remote_mcp(config: RemoteMcpConfig) -> None:
    """Serve JSON-RPC MCP requests over HTTP."""

    httpd = make_remote_mcp_http_server(config)
    httpd.serve_forever()


def make_remote_mcp_http_server(config: RemoteMcpConfig) -> ThreadingHTTPServer:
    """Build a remote MCP HTTP server without starting it."""

    mcp_server = ReadOnlyMcpServer(kb_root=config.kb_root, agent=config.agent)
    handler = _build_handler(mcp_server=mcp_server, config=config)
    return ThreadingHTTPServer((config.host, config.port), handler)


def handle_remote_jsonrpc(
    *,
    kb_root: Path,
    agent: str,
    payload: dict[str, Any],
) -> dict[str, Any] | None:
    """Handle one JSON-RPC payload without HTTP; used by tests."""

    return ReadOnlyMcpServer(kb_root=kb_root, agent=agent).handle_request(payload)


def _build_handler(
    *,
    mcp_server: ReadOnlyMcpServer,
    config: RemoteMcpConfig,
) -> type[BaseHTTPRequestHandler]:
    class LintaRemoteMcpHandler(BaseHTTPRequestHandler):
        server_version = f"LintaRemoteMCP/{__version__}"

        def do_GET(self) -> None:
            if self.path != "/health":
                self._write_json(404, {"error": "not_found"})
                return
            self._write_json(
                200,
                {
                    "ok": True,
                    "name": "linta",
                    "version": __version__,
                    "agent": config.agent,
                },
            )

        def do_POST(self) -> None:
            if self.path != config.path:
                self._write_json(404, {"error": "not_found"})
                return
            if not _is_authorized(self.headers.get("Authorization"), config.token):
                self._write_json(
                    401,
                    {"error": "unauthorized"},
                    headers={"WWW-Authenticate": 'Bearer realm="linta-remote-mcp"'},
                )
                return
            length = int(self.headers.get("Content-Length") or "0")
            if length <= 0:
                self._write_json(400, {"error": "empty_request"})
                return
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
            except json.JSONDecodeError as error:
                self._write_json(400, {"error": "invalid_json", "message": str(error)})
                return
            response = mcp_server.handle_request(payload)
            if response is None:
                self._write_json(202, {"ok": True})
                return
            self._write_json(200, response)

        def log_message(self, format: str, *args: object) -> None:
            return

        def _write_json(
            self,
            status: int,
            payload: dict[str, Any],
            *,
            headers: dict[str, str] | None = None,
        ) -> None:
            body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            for key, value in (headers or {}).items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(body)

    return LintaRemoteMcpHandler


def _is_authorized(header: str | None, token: str) -> bool:
    if not header:
        return False
    scheme, _, value = header.partition(" ")
    return scheme.lower() == "bearer" and value.strip() == token
