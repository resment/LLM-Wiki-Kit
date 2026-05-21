import json
from pathlib import Path

from typer.testing import CliRunner

from linta.agent_access import configure_agent_access, set_agent_access
from linta.cli import app
from linta.init_kb import init_knowledge_base
from linta.mcp_server import ReadOnlyMcpServer
from linta.remote_mcp import _is_authorized, handle_remote_jsonrpc, token_from_env

runner = CliRunner()


def test_write_tools_are_exposed_only_for_write_policy(tmp_path: Path) -> None:
    kb = tmp_path / "kb"
    init_knowledge_base(kb)
    configure_agent_access(kb, primary_agent="hermes")

    read_server = ReadOnlyMcpServer(kb_root=kb, agent="claude-desktop")
    assert "write_current_draft" not in {tool["name"] for tool in read_server.list_tools()}

    set_agent_access(kb, agent="claude-desktop", mode="write", read_scope="wiki-context")
    write_server = ReadOnlyMcpServer(kb_root=kb, agent="claude-desktop")
    assert "write_current_draft" in {tool["name"] for tool in write_server.list_tools()}


def test_write_current_draft_stays_inside_current_draft(tmp_path: Path) -> None:
    kb = tmp_path / "kb"
    init_knowledge_base(kb)
    configure_agent_access(kb, primary_agent="hermes")
    set_agent_access(kb, agent="claude-desktop", mode="write", read_scope="wiki-context")
    server = ReadOnlyMcpServer(kb_root=kb, agent="claude-desktop")

    result = server.call_tool(
        "write_current_draft",
        {"path": "project-alpha.md", "content": "# Project Alpha\n"},
    )

    payload = json.loads(result["content"][0]["text"])
    assert payload["path"] == "ai_kb/wiki/current_draft/project-alpha.md"
    assert (kb / "ai_kb/wiki/current_draft/project-alpha.md").read_text(
        encoding="utf-8"
    ) == "# Project Alpha\n"

    denied = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "write_current_draft",
                "arguments": {"path": "ai_kb/raw/docs/x.md", "content": "# X\n"},
            },
        }
    )
    assert denied is not None
    assert "Draft path not allowed" in denied["error"]["message"]


def test_propose_wiki_patch_stores_reviewable_patch(tmp_path: Path) -> None:
    kb = tmp_path / "kb"
    init_knowledge_base(kb)
    configure_agent_access(kb, primary_agent="hermes")
    set_agent_access(kb, agent="claude-desktop", mode="write", read_scope="wiki-context")
    server = ReadOnlyMcpServer(kb_root=kb, agent="claude-desktop")

    result = server.call_tool(
        "propose_wiki_patch",
        {
            "title": "Project Alpha update",
            "target_path": "ai_kb/wiki/current/project-alpha.md",
            "patch": "--- old\n+++ new\n@@\n-Old\n+New",
            "notes": "Review before applying.",
        },
    )

    payload = json.loads(result["content"][0]["text"])
    patch_path = kb / payload["path"]
    text = patch_path.read_text(encoding="utf-8")
    assert payload["path"] == "ai_kb/wiki/current_draft/patches/project-alpha-update.patch.md"
    assert "Review before applying." in text
    assert "```diff" in text


def test_remote_mcp_auth_helper_and_jsonrpc_handler(tmp_path: Path) -> None:
    kb = tmp_path / "kb"
    init_knowledge_base(kb)
    configure_agent_access(kb, primary_agent="hermes")

    assert not _is_authorized(None, "secret-token")
    assert not _is_authorized("Bearer wrong-token", "secret-token")
    assert _is_authorized("Bearer secret-token", "secret-token")

    payload = handle_remote_jsonrpc(
        kb_root=kb,
        agent="claude-desktop",
        payload={"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
    )

    assert payload is not None
    assert payload["id"] == 2
    assert any(tool["name"] == "context_overview" for tool in payload["result"]["tools"])


def test_remote_token_env_and_cli_error(monkeypatch) -> None:
    monkeypatch.setenv("LINTA_REMOTE_MCP_TOKEN", "token")
    assert token_from_env() == "token"
    monkeypatch.delenv("LINTA_REMOTE_MCP_TOKEN")

    result = runner.invoke(app, ["mcp", "serve-http", "--kb-root", "."])

    assert result.exit_code == 2
    assert "Missing bearer token" in result.output
