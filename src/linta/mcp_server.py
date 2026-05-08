"""Minimal read-only MCP server for Linta."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from linta import __version__
from linta.agent_access import (
    WIKI_CONTEXT_PATHS,
    AgentPolicy,
    agent_access_json,
    is_read_allowed,
    list_allowed_context_files,
    read_agent_access_config,
    read_agent_policy,
)
from linta.doctor import doctor_json, run_doctor
from linta.linting import lint_knowledge_base

READ_ONLY_TOOLS = (
    "doctor",
    "agent_status",
    "list_context_files",
    "read_context_file",
    "search_context",
    "read_indexes",
    "read_manifest",
    "read_source_card",
    "context_overview",
    "context_search",
    "context_read",
    "context_bundle",
)

PRACTICAL_CONTEXT_TOOLS = (
    "context_overview",
    "context_search",
    "context_read",
    "context_bundle",
)

PRACTICAL_CONTEXT_POLICY = AgentPolicy(mode="read", read_scope="wiki_context")
CONTEXT_BUNDLE_DEFAULT_LIMIT = 8
CONTEXT_BUNDLE_MAX_LIMIT = 20


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
                "Run read-only Linta diagnostics.",
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
            _tool(
                "context_overview",
                "Summarize the practical Claude-readable Linta context surface.",
                {},
            ),
            _tool(
                "context_search",
                "Search practical Linta context without reading raw sources.",
                {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": CONTEXT_BUNDLE_MAX_LIMIT},
                },
                required=["query"],
            ),
            _tool(
                "context_read",
                "Read one practical Linta context file; raw sources are always denied.",
                {"path": {"type": "string"}},
                required=["path"],
            ),
            _tool(
                "context_bundle",
                "Build a practical context package from a query or explicit context paths.",
                {
                    "query": {"type": "string"},
                    "paths": {"type": "array", "items": {"type": "string"}},
                    "limit": {"type": "integer", "minimum": 1, "maximum": CONTEXT_BUNDLE_MAX_LIMIT},
                },
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
        if name == "context_overview":
            return _json_result(self._context_overview())
        if name == "context_search":
            return _json_result(
                {
                    "matches": self._context_search(
                        str(args.get("query") or ""),
                        limit=_limit(args.get("limit")),
                    )
                }
            )
        if name == "context_read":
            return _text_result(self._read_practical_context(str(args.get("path") or "")))
        if name == "context_bundle":
            return _json_result(
                self._context_bundle(
                    query=str(args.get("query") or ""),
                    paths=args.get("paths"),
                    limit=_limit(args.get("limit")),
                )
            )
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
                    "serverInfo": {"name": "linta", "version": __version__},
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

    def _context_overview(self) -> dict[str, Any]:
        files = self._practical_context_files()
        return {
            "kb_root": self.kb_root.as_posix(),
            "agent": self.agent,
            "boundary": (
                "Practical context tools read compiled wiki context only. "
                "They do not read ai_kb/raw, human, archive, or current_draft."
            ),
            "policy": self.policy.to_dict(),
            "practical_tools": list(PRACTICAL_CONTEXT_TOOLS),
            "entrypoints": {
                "current": self._path_status("ai_kb/wiki/current"),
                "portfolio": self._path_status("ai_kb/wiki/portfolio"),
                "manifest": self._path_status("ai_kb/wiki/source_manifest.md"),
                "source_cards": self._path_status("ai_kb/wiki/source_cards"),
                "indexes": self._path_status("ai_kb/wiki/indexes"),
            },
            "freshness": self._context_freshness(),
            "files": files,
        }

    def _context_search(self, query: str, *, limit: int) -> list[dict[str, Any]]:
        if not query:
            raise McpError("Query must not be empty.")
        matches: list[dict[str, Any]] = []
        for relative in self._practical_context_files():
            path = self.kb_root / relative
            text = path.read_text(encoding="utf-8")
            for index, line in enumerate(text.splitlines(), start=1):
                if query.lower() not in line.lower():
                    continue
                matches.append(
                    {
                        "path": relative,
                        "content_type": _content_type(relative),
                        "line": index,
                        "snippet": line.strip(),
                    }
                )
                if len(matches) >= limit:
                    return matches
        return matches

    def _context_bundle(
        self,
        *,
        query: str,
        paths: object,
        limit: int,
    ) -> dict[str, Any]:
        selected = _string_list(paths)
        if not selected and query:
            selected = _unique(
                [match["path"] for match in self._context_search(query, limit=limit)]
            )
        if not selected:
            selected = self._default_context_entrypoints(limit=limit)
        selected = selected[:limit]
        files = []
        for relative in selected:
            text = self._read_practical_context(relative)
            files.append(
                {
                    "path": relative,
                    "content_type": _content_type(relative),
                    "text": text,
                }
            )
        freshness = self._context_freshness()
        return {
            "kb_root": self.kb_root.as_posix(),
            "query": query,
            "boundary": (
                "This bundle contains compiled Linta context only. Raw sources are excluded."
            ),
            "freshness": freshness,
            "warnings": freshness["warnings"],
            "files": files,
            "source_cards": [
                path for path in selected if path.startswith("ai_kb/wiki/source_cards/")
            ],
            "indexes": [path for path in selected if path.startswith("ai_kb/wiki/indexes/")],
        }

    def _context_freshness(self) -> dict[str, Any]:
        issues = lint_knowledge_base(self.kb_root)
        errors = [issue for issue in issues if issue.severity == "error"]
        warnings = [issue for issue in issues if issue.severity == "warning"]
        warning_messages = _freshness_warnings(self.kb_root, issues)
        return {
            "ok": not errors,
            "indexes_present": _has_json_files(self.kb_root / "ai_kb/wiki/indexes"),
            "current_pages": _count_markdown_files(self.kb_root / "ai_kb/wiki/current"),
            "missing_source_cards": [
                issue.path for issue in issues if issue.code == "missing-source-card"
            ],
            "manifest_issues": [
                issue.path
                for issue in issues
                if issue.code in {"raw-not-in-manifest", "manifest-source-missing"}
            ],
            "stale_current": [issue.path for issue in issues if issue.code == "stale-current"],
            "lint_issue_count": len(issues),
            "lint_error_count": len(errors),
            "lint_warning_count": len(warnings),
            "warnings": warning_messages,
            "recommended_action": (
                "Ask the primary writer Agent to run linta maintenance daily before relying on "
                "this context."
                if warning_messages
                else "Context freshness signals are clean."
            ),
        }

    def _default_context_entrypoints(self, *, limit: int) -> list[str]:
        preferred = (
            "README.md",
            "AGENTS.md",
            "ai_kb/schema/AGENTS.md",
            "ai_kb/wiki/source_manifest.md",
        )
        files = self._practical_context_files()
        selected = [path for path in preferred if path in files]
        for path in files:
            if path not in selected:
                selected.append(path)
            if len(selected) >= limit:
                break
        return selected

    def _read_practical_context(self, relative_path: str) -> str:
        path = (self.kb_root / relative_path).resolve()
        if not self._is_practical_context_allowed(path):
            raise McpError(f"Practical context read not allowed: {relative_path}")
        if not path.is_file():
            raise McpError(f"File does not exist: {relative_path}")
        return path.read_text(encoding="utf-8")

    def _practical_context_files(self) -> list[str]:
        files: set[str] = set()
        for relative in WIKI_CONTEXT_PATHS:
            path = (self.kb_root / relative).resolve()
            if path.is_file() and self._is_practical_context_allowed(path):
                files.add(path.relative_to(self.kb_root).as_posix())
            elif path.is_dir():
                for child in path.rglob("*"):
                    if child.is_file() and self._is_practical_context_allowed(child):
                        files.add(child.relative_to(self.kb_root).as_posix())
        return sorted(files)

    def _is_practical_context_allowed(self, path: Path) -> bool:
        return is_read_allowed(
            self.kb_root,
            self.policy,
            path,
        ) and is_read_allowed(self.kb_root, PRACTICAL_CONTEXT_POLICY, path)

    def _path_status(self, relative_path: str) -> dict[str, Any]:
        path = self.kb_root / relative_path
        allowed = self._is_practical_context_allowed(path.resolve())
        if path.is_file():
            count = 1
        elif path.is_dir():
            count = sum(
                1
                for child in path.rglob("*")
                if child.is_file() and self._is_practical_context_allowed(child)
            )
        else:
            count = 0
        return {"exists": path.exists(), "allowed": allowed, "file_count": count}

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


def _limit(value: object) -> int:
    try:
        raw = int(value) if value is not None else CONTEXT_BUNDLE_DEFAULT_LIMIT
    except (TypeError, ValueError):
        raw = CONTEXT_BUNDLE_DEFAULT_LIMIT
    return max(1, min(raw, CONTEXT_BUNDLE_MAX_LIMIT))


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _content_type(relative_path: str) -> str:
    if relative_path.startswith("ai_kb/wiki/current/"):
        return "current"
    if relative_path.startswith("ai_kb/wiki/portfolio/"):
        return "portfolio"
    if relative_path.startswith("ai_kb/wiki/source_cards/"):
        return "source_card"
    if relative_path.startswith("ai_kb/wiki/indexes/"):
        return "index"
    if relative_path == "ai_kb/wiki/source_manifest.md":
        return "manifest"
    if relative_path.startswith("ai_kb/schema/"):
        return "schema"
    return "wiki_context"


def _freshness_warnings(kb_root: Path, issues: list[Any]) -> list[str]:
    warnings: list[str] = []
    if not _has_json_files(kb_root / "ai_kb/wiki/indexes"):
        warnings.append(
            "Indexes are missing; ask the primary writer Agent to run linta index build."
        )
    if not _has_markdown_files(kb_root / "ai_kb/wiki/current"):
        warnings.append("Confirmed current context is missing.")
    if any(issue.code == "missing-source-card" for issue in issues):
        warnings.append("Some raw sources are missing source cards.")
    if any(issue.code in {"raw-not-in-manifest", "manifest-source-missing"} for issue in issues):
        warnings.append("Manifest and raw sources are inconsistent.")
    if any(issue.code == "stale-current" for issue in issues):
        warnings.append("Some confirmed current pages may be stale.")
    if any(issue.severity == "error" for issue in issues):
        warnings.append("Deterministic lint errors are present.")
    return warnings


def _has_json_files(path: Path) -> bool:
    return path.exists() and any(path.glob("*.json"))


def _has_markdown_files(path: Path) -> bool:
    return path.exists() and any(path.rglob("*.md"))


def _count_markdown_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for child in path.rglob("*.md") if child.is_file())
