import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from llm_wiki_kit.agent_access import (
    access_config_path,
    configure_agent_access,
    is_read_allowed,
    list_allowed_context_files,
    read_agent_access_config,
    set_agent_access,
)
from llm_wiki_kit.claude_desktop import render_claude_desktop_config
from llm_wiki_kit.cli import app
from llm_wiki_kit.doctor import run_doctor
from llm_wiki_kit.init_kb import init_knowledge_base
from llm_wiki_kit.mcp_server import READ_ONLY_TOOLS, ReadOnlyMcpServer

runner = CliRunner()


def test_configure_agent_access_creates_default_policy(tmp_path: Path) -> None:
    kb = tmp_path / "kb"
    init_knowledge_base(kb)

    result = configure_agent_access(kb, primary_agent="hermes")

    assert result.path == kb.resolve() / ".llm-wiki/agent_access.yaml"
    config = read_agent_access_config(kb)
    assert config.primary_agent == "hermes"
    assert config.agents["hermes"].mode == "write"
    assert config.agents["claude_desktop"].mode == "read"
    assert config.agents["claude_desktop"].read_scope == "wiki_context"


def test_agent_access_refuses_existing_without_force(tmp_path: Path) -> None:
    kb = tmp_path / "kb"
    init_knowledge_base(kb)
    configure_agent_access(kb, primary_agent="hermes")

    with pytest.raises(FileExistsError):
        configure_agent_access(kb, primary_agent="codex")

    result = configure_agent_access(kb, primary_agent="codex", force=True)

    assert result.config.primary_agent == "codex"
    assert result.config.agents["codex"].mode == "write"
    assert result.config.agents["hermes"].mode == "read"


def test_agent_set_updates_single_policy_and_primary_writer(tmp_path: Path) -> None:
    kb = tmp_path / "kb"
    init_knowledge_base(kb)
    configure_agent_access(kb, primary_agent="hermes")

    set_agent_access(kb, agent="claude-desktop", mode="write", read_scope="full-kb")

    config = read_agent_access_config(kb)
    assert config.primary_agent == "claude_desktop"
    assert config.agents["claude_desktop"].mode == "write"
    assert config.agents["hermes"].mode == "read"


def test_agent_set_refuses_to_remove_only_writer(tmp_path: Path) -> None:
    kb = tmp_path / "kb"
    init_knowledge_base(kb)
    configure_agent_access(kb, primary_agent="hermes")

    with pytest.raises(ValueError, match="At least one agent"):
        set_agent_access(kb, agent="hermes", mode="read", read_scope="wiki-context")


def test_cli_agents_wizard_status_policy_and_set(tmp_path: Path) -> None:
    kb = tmp_path / "kb"
    init_knowledge_base(kb)

    wizard = runner.invoke(app, ["agents", "wizard", str(kb)], input="codex\n")

    assert wizard.exit_code == 0, wizard.output
    assert "codex" in wizard.output
    assert access_config_path(kb).is_file()

    status = runner.invoke(app, ["agents", "status", str(kb), "--json"])
    assert status.exit_code == 0, status.output
    assert json.loads(status.output)["primary_agent"] == "codex"

    update = runner.invoke(
        app,
        [
            "agents",
            "set",
            str(kb),
            "--agent",
            "openclaw",
            "--mode",
            "read",
            "--read-scope",
            "exports-only",
        ],
    )
    assert update.exit_code == 0, update.output

    policy = runner.invoke(
        app,
        ["agents", "policy", str(kb), "--agent", "openclaw", "--json"],
    )
    assert policy.exit_code == 0, policy.output
    payload = json.loads(policy.output)
    assert payload["agent"] == "openclaw"
    assert payload["read_scope"] == "exports_only"


def test_doctor_warns_when_agent_access_policy_missing(tmp_path: Path) -> None:
    kb = tmp_path / "kb"
    init_knowledge_base(kb)

    report = run_doctor(kb)

    assert any(check.code == "agent-access-missing" for check in report.checks)


def test_claude_desktop_config_and_status(tmp_path: Path) -> None:
    kb = tmp_path / "kb"
    init_knowledge_base(kb)
    configure_agent_access(kb, primary_agent="hermes")

    snippet = json.loads(render_claude_desktop_config(kb))
    args = snippet["mcpServers"]["llm-wiki-kit"]["args"]
    assert args[:2] == ["mcp", "serve"]
    assert "claude-desktop" in args

    result = runner.invoke(app, ["claude-desktop", "status", str(kb), "--json"])
    assert result.exit_code == 0, result.output
    status = json.loads(result.output)
    assert status["policy_mode"] == "read"
    assert status["read_scope"] == "wiki_context"


def test_read_policy_blocks_raw_and_allows_wiki_context(tmp_path: Path) -> None:
    kb = tmp_path / "kb"
    init_knowledge_base(kb)
    configure_agent_access(kb, primary_agent="hermes")
    policy = read_agent_access_config(kb).agents["claude_desktop"]

    assert is_read_allowed(kb, policy, kb / "ai_kb/wiki/source_manifest.md")
    assert not is_read_allowed(kb, policy, kb / "ai_kb/raw/docs/source.md")

    files = list_allowed_context_files(kb, policy)
    assert "ai_kb/wiki/source_manifest.md" in files
    assert all(not path.startswith("ai_kb/raw/") for path in files)


def test_mcp_server_only_exposes_read_tools_and_enforces_policy(tmp_path: Path) -> None:
    kb = tmp_path / "kb"
    init_knowledge_base(kb)
    configure_agent_access(kb, primary_agent="hermes")
    server = ReadOnlyMcpServer(kb_root=kb, agent="claude-desktop")

    tool_names = {tool["name"] for tool in server.list_tools()}

    assert tool_names == set(READ_ONLY_TOOLS)
    assert "raw_import" not in tool_names
    assert "# Source Manifest" in server.call_tool("read_manifest")["content"][0]["text"]
    denied = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "read_context_file", "arguments": {"path": "ai_kb/raw/docs/x.md"}},
        }
    )
    assert denied is not None
    assert "Read not allowed" in denied["error"]["message"]
