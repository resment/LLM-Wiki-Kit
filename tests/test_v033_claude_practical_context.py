import json
from pathlib import Path

from typer.testing import CliRunner

from linta.agent_access import configure_agent_access, set_agent_access
from linta.cli import app
from linta.init_kb import init_knowledge_base
from linta.mcp_server import PRACTICAL_CONTEXT_TOOLS, ReadOnlyMcpServer

runner = CliRunner()


def test_context_overview_reports_practical_surface(tmp_path: Path) -> None:
    kb = tmp_path / "kb"
    init_knowledge_base(kb)
    configure_agent_access(kb, primary_agent="hermes")
    (kb / "ai_kb/wiki/current/summary.md").write_text(
        "# Current Summary\n\nProject Alpha is active.\n",
        encoding="utf-8",
    )

    server = ReadOnlyMcpServer(kb_root=kb, agent="claude-desktop")
    payload = _json_tool(server, "context_overview")

    assert payload["practical_tools"] == list(PRACTICAL_CONTEXT_TOOLS)
    assert payload["entrypoints"]["current"]["file_count"] == 1
    assert payload["entrypoints"]["entities"]["file_count"] == 4
    assert "ai_kb/wiki/current/summary.md" in payload["files"]
    assert "ai_kb/raw" in payload["boundary"]


def test_context_search_and_read_exclude_raw_sources(tmp_path: Path) -> None:
    kb = tmp_path / "kb"
    init_knowledge_base(kb)
    configure_agent_access(kb, primary_agent="hermes")
    (kb / "ai_kb/wiki/current/alpha.md").write_text(
        "# Alpha\n\nReviewed project context.\n",
        encoding="utf-8",
    )
    (kb / "ai_kb/raw/docs/raw-alpha.md").write_text(
        "# Raw Alpha\n\nRaw secret project context.\n",
        encoding="utf-8",
    )

    server = ReadOnlyMcpServer(kb_root=kb, agent="claude-desktop")
    payload = _json_tool(server, "context_search", {"query": "project", "limit": 10})

    paths = {match["path"] for match in payload["matches"]}
    assert "ai_kb/wiki/current/alpha.md" in paths
    assert "ai_kb/raw/docs/raw-alpha.md" not in paths
    assert "Reviewed project context" in server.call_tool(
        "context_read", {"path": "ai_kb/wiki/current/alpha.md"}
    )["content"][0]["text"]
    denied = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "context_read",
                "arguments": {"path": "ai_kb/raw/docs/raw-alpha.md"},
            },
        }
    )
    assert denied is not None
    assert "Practical context read not allowed" in denied["error"]["message"]


def test_context_bundle_builds_query_package(tmp_path: Path) -> None:
    kb = tmp_path / "kb"
    init_knowledge_base(kb)
    configure_agent_access(kb, primary_agent="hermes")
    (kb / "ai_kb/wiki/portfolio/projects.md").write_text(
        "# Projects\n\nProject Alpha depends on Capability Review.\n",
        encoding="utf-8",
    )
    (kb / "ai_kb/wiki/source_cards/alpha.md").write_text(
        "# Source Card Alpha\n\nCompiled evidence for Project Alpha.\n",
        encoding="utf-8",
    )

    server = ReadOnlyMcpServer(kb_root=kb, agent="claude-desktop")
    payload = _json_tool(server, "context_bundle", {"query": "Alpha", "limit": 5})

    paths = [file["path"] for file in payload["files"]]
    assert "ai_kb/wiki/portfolio/projects.md" in paths
    assert "ai_kb/wiki/source_cards/alpha.md" in paths
    assert "Raw sources are excluded" in payload["boundary"]


def test_context_search_and_bundle_include_entity_context(tmp_path: Path) -> None:
    kb = tmp_path / "kb"
    init_knowledge_base(kb)
    configure_agent_access(kb, primary_agent="hermes")
    entity = kb / "ai_kb/wiki/entities/people/alex-reviewer.md"
    entity.write_text(
        """---
title: Alex Reviewer
entity_type: person
entity_id: person.alex-reviewer
aliases: [Alex]
---

# Alex Reviewer

Alex participates in Review Routing.
""",
        encoding="utf-8",
    )

    server = ReadOnlyMcpServer(kb_root=kb, agent="claude-desktop")
    search_payload = _json_tool(server, "context_search", {"query": "Review Routing", "limit": 10})
    paths = {match["path"] for match in search_payload["matches"]}
    assert "ai_kb/wiki/entities/people/alex-reviewer.md" in paths

    bundle_payload = _json_tool(server, "context_bundle", {"query": "Review Routing", "limit": 5})
    bundled_paths = [file["path"] for file in bundle_payload["files"]]
    assert "ai_kb/wiki/entities/people/alex-reviewer.md" in bundled_paths


def test_practical_context_ignores_full_kb_raw_access(tmp_path: Path) -> None:
    kb = tmp_path / "kb"
    init_knowledge_base(kb)
    configure_agent_access(kb, primary_agent="hermes")
    set_agent_access(kb, agent="claude-desktop", mode="read", read_scope="full-kb")
    (kb / "ai_kb/raw/docs/raw.md").write_text("# Raw\n\nNeedle only in raw.\n", encoding="utf-8")

    server = ReadOnlyMcpServer(kb_root=kb, agent="claude-desktop")

    assert "Needle only in raw" in server.call_tool(
        "read_context_file", {"path": "ai_kb/raw/docs/raw.md"}
    )["content"][0]["text"]
    payload = _json_tool(server, "context_search", {"query": "Needle", "limit": 10})
    assert payload["matches"] == []


def test_claude_status_reports_practical_tools_and_warnings(tmp_path: Path) -> None:
    kb = tmp_path / "kb"
    init_knowledge_base(kb)
    configure_agent_access(kb, primary_agent="hermes")

    result = runner.invoke(app, ["claude-desktop", "status", str(kb), "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["practical_context_tools"] == list(PRACTICAL_CONTEXT_TOOLS)
    assert "Indexes are missing" in payload["warnings"][0]


def _json_tool(
    server: ReadOnlyMcpServer,
    name: str,
    arguments: dict[str, object] | None = None,
) -> dict[str, object]:
    text = server.call_tool(name, arguments or {})["content"][0]["text"]
    return json.loads(text)
