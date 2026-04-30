"""Minimal read-only MCP server for llm-wiki-kit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from llm_wiki_kit import __version__
from llm_wiki_kit.agent_access import (
    agent_access_json,
    is_read_allowed,
    list_allowed_context_files,
    read_agent_access_config,
    read_agent_policy,
)
from llm_wiki_kit.doctor import doctor_json, run_doctor

READ_ONLY_TOOLS = (
    "doctor",
    "agent_status",
    "list_context_files",
    "read_context_file",
    "search_context",
    "read_indexes",
    "read_manifest",
    "read_source_card",
)


class McpError(Exception):
    """MCP tool error."""


class ReadOnlyMcpServer:
    def __init__(self, *, kb_root: Path, agent: str) -> None:
        self.kb_root = kb_root.expanduser().resolve()
        self.agent = agent
        self.policy = read_agent_policy(self.kb_root, agent)

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            _tool(
                "doctor",
                "Run read-only llm-wiki-kit diagnostics.",
                {},
            ),
            _tool(
                "agent_status",
                "Show the configured access policy for this MCP agent.",
                {},
            ),
            _tool(
                "list_context_files",
                "List files this agent is allowed to read.",
                {},
            ),
            _tool(
                "read_context_file",
                "Read one allowed Markdown or JSON context file.",
                {"path": {"type": "string"}},
                required=["path"],
            ),
            _tool(
                "search_context",
                "Search allowed context files for plain text.",
                {"query": {"type": "string"}},
                required=["query"],
            ),
            _tool("read_indexes", "Read generated JSON indexes.", {}),
            _tool("read_manifest", "Read the source manifest.", {}),
            _tool(
                "read_source_card",
                "Read one source card by relative path or filename.",
                {"path": {"type": "string"}},
                required=["path"],
            ),
        ]

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        if name not in READ_ONLY_TOOLS:
            raise McpError(f"Unknown or disallowed tool: {name}")
        args = arguments or {}
        if name == "doctor":
            return _text_result(doctor_json(run_doctor(self.kb_root)))
        if name == "agent_status":
            return _text_result(agent_access_json(read_agent_access_config(self.kb_root)))
        if name == "list_context_files":
            return _json_result({"files": list_allowed_context_files(self.kb_root, self.policy)})
        if name == "read_context_file":
            return _text_result(self._read_allowed(str(args.get("path") or "")))
        if name == "search_context":
            return _json_result({"matches": self._search(str(args.get("query") or ""))})
        if name == "read_indexes":
            return _json_result(self._read_directory_json("ai_kb/wiki/indexes"))
        if name == "read_manifest":
            return _text_result(self._read_allowed("ai_kb/wiki/source_manifest.md"))
        if name == "read_source_card":
            return _text_result(self._read_source_card(str(args.get("path") or "")))
        raise McpError(f"Unhandled tool: {name}")

    def handle_request(self, request: dict[str, Any]) -> dict[str, Any] | None:
        method = request.get("method")
        request_id = request.get("id")
        if method == "notifications/initialized":
            return None
        try:
            if method == "initialize":
                result = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "llm-wiki-kit", "version": __version__},
                }
            elif method == "tools/list":
                result = {"tools": self.list_tools()}
            elif method == "tools/call":
                params = request.get("params") or {}
                result = self.call_tool(
                    str(params.get("name") or ""),
                    params.get("arguments") or {},
                )
            else:
                raise McpError(f"Unsupported method: {method}")
            return {"jsonrpc": "2.0", "id": request_id, "result": result}
        except Exception as error:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32000, "message": str(error)},
            }

    def _read_allowed(self, relative_path: str) -> str:
        path = (self.kb_root / relative_path).resolve()
        if not is_read_allowed(self.kb_root, self.policy, path):
            raise McpError(f"Read not allowed: {relative_path}")
        if not path.is_file():
            raise McpError(f"File does not exist: {relative_path}")
        return path.read_text(encoding="utf-8")

    def _search(self, query: str) -> list[dict[str, Any]]:
        if not query:
            raise McpError("Query must not be empty.")
        matches: list[dict[str, Any]] = []
        for relative in list_allowed_context_files(self.kb_root, self.policy):
            path = self.kb_root / relative
            text = path.read_text(encoding="utf-8")
            lines = [
                {"line": index, "text": line}
                for index, line in enumerate(text.splitlines(), start=1)
                if query.lower() in line.lower()
            ]
            if lines:
                matches.append({"path": relative, "matches": lines[:20]})
        return matches

    def _read_directory_json(self, relative_directory: str) -> dict[str, Any]:
        directory = (self.kb_root / relative_directory).resolve()
        if not is_read_allowed(self.kb_root, self.policy, directory):
            raise McpError(f"Read not allowed: {relative_directory}")
        result: dict[str, Any] = {}
        if not directory.exists():
            return result
        for path in sorted(directory.glob("*.json")):
            result[path.name] = json.loads(path.read_text(encoding="utf-8"))
        return result

    def _read_source_card(self, requested_path: str) -> str:
        if not requested_path:
            raise McpError("Source card path must not be empty.")
        path = Path(requested_path)
        if not path.parts or path.parts[0] != "ai_kb":
            path = Path("ai_kb/wiki/source_cards") / path
        return self._read_allowed(path.as_posix())


def serve_mcp_stdio(*, kb_root: Path, agent: str) -> None:
    server = ReadOnlyMcpServer(kb_root=kb_root, agent=agent)
    while True:
        request = _read_message(sys.stdin.buffer)
        if request is None:
            return
        response = server.handle_request(request)
        if response is not None:
            _write_message(sys.stdout.buffer, response)


def _read_message(stream: Any) -> dict[str, Any] | None:
    headers: dict[str, str] = {}
    while True:
        line = stream.readline()
        if line == b"":
            return None
        text = line.decode("utf-8").strip()
        if not text:
            break
        key, _, value = text.partition(":")
        headers[key.lower()] = value.strip()
    length = int(headers.get("content-length") or "0")
    if length <= 0:
        return None
    return json.loads(stream.read(length).decode("utf-8"))


def _write_message(stream: Any, message: dict[str, Any]) -> None:
    payload = json.dumps(message, separators=(",", ":")).encode("utf-8")
    stream.write(f"Content-Length: {len(payload)}\r\n\r\n".encode())
    stream.write(payload)
    stream.flush()


def _tool(
    name: str,
    description: str,
    properties: dict[str, Any],
    *,
    required: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "description": description,
        "inputSchema": {
            "type": "object",
            "properties": properties,
            "required": required or [],
        },
    }


def _text_result(text: str) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def _json_result(value: dict[str, Any]) -> dict[str, Any]:
    return _text_result(json.dumps(value, indent=2) + "\n")
