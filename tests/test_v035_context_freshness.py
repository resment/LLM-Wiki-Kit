import json
from pathlib import Path

from linta.agent_access import configure_agent_access
from linta.claude_desktop import build_claude_project_instructions
from linta.init_kb import init_knowledge_base
from linta.mcp_server import ReadOnlyMcpServer


def test_context_overview_reports_freshness_warnings(tmp_path: Path) -> None:
    kb = tmp_path / "kb"
    init_knowledge_base(kb)
    configure_agent_access(kb, primary_agent="hermes")
    (kb / "ai_kb/raw/docs/source.md").write_text("# Source\n", encoding="utf-8")

    server = ReadOnlyMcpServer(kb_root=kb, agent="claude-desktop")
    payload = _json_tool(server, "context_overview")

    freshness = payload["freshness"]
    assert freshness["indexes_present"] is False
    assert freshness["current_pages"] == 0
    assert "ai_kb/raw/docs/source.md" in freshness["missing_source_cards"]
    assert any("Indexes are missing" in warning for warning in freshness["warnings"])
    assert any(
        "Confirmed current context is missing" in warning for warning in freshness["warnings"]
    )
    assert "maintenance daily" in freshness["recommended_action"]


def test_context_bundle_includes_freshness_warnings(tmp_path: Path) -> None:
    kb = tmp_path / "kb"
    init_knowledge_base(kb)
    configure_agent_access(kb, primary_agent="hermes")
    (kb / "ai_kb/wiki/current/alpha.md").write_text(
        "# Alpha\n\nCompiled project context.\n",
        encoding="utf-8",
    )

    server = ReadOnlyMcpServer(kb_root=kb, agent="claude-desktop")
    payload = _json_tool(server, "context_bundle", {"query": "project"})

    assert payload["freshness"]["current_pages"] == 1
    assert payload["warnings"] == payload["freshness"]["warnings"]
    assert any("Indexes are missing" in warning for warning in payload["warnings"])


def test_project_instructions_mention_freshness_maintenance(tmp_path: Path) -> None:
    kb = tmp_path / "kb"
    init_knowledge_base(kb)

    instructions = build_claude_project_instructions(kb).instructions

    assert "freshness warnings" in instructions
    assert "linta maintenance daily" in instructions


def _json_tool(
    server: ReadOnlyMcpServer,
    name: str,
    arguments: dict[str, object] | None = None,
) -> dict[str, object]:
    text = server.call_tool(name, arguments or {})["content"][0]["text"]
    return json.loads(text)
