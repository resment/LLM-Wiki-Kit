"""Claude Desktop configuration helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from linta.agent_access import read_agent_policy
from linta.doctor import run_doctor
from linta.mcp_server import PRACTICAL_CONTEXT_TOOLS

READ_BOUNDARY = (
    "Use compiled Linta wiki context only. Do not request or read ai_kb/raw, human, archive, "
    "or ai_kb/wiki/current_draft through Claude Project work."
)


@dataclass(frozen=True)
class ClaudeDesktopStatus:
    kb_root: Path
    policy_mode: str
    read_scope: str
    kb_ok: bool
    practical_context_tools: list[str]
    project_instructions_available: bool
    warnings: list[str]
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "kb_root": self.kb_root.as_posix(),
            "policy_mode": self.policy_mode,
            "read_scope": self.read_scope,
            "kb_ok": self.kb_ok,
            "practical_context_tools": self.practical_context_tools,
            "project_instructions_available": self.project_instructions_available,
            "warnings": self.warnings,
            "message": self.message,
        }


@dataclass(frozen=True)
class ClaudeProjectInstructions:
    kb_root: Path
    instructions: str
    tools: list[str]
    read_boundary: str
    recommended_first_prompt: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "kb_root": self.kb_root.as_posix(),
            "instructions": self.instructions,
            "tools": self.tools,
            "read_boundary": self.read_boundary,
            "recommended_first_prompt": self.recommended_first_prompt,
        }


def render_claude_desktop_config(kb_root: Path) -> str:
    root = kb_root.expanduser().resolve()
    config = {
        "mcpServers": {
            "linta": {
                "command": "linta",
                "args": [
                    "mcp",
                    "serve",
                    "--agent",
                    "claude-desktop",
                    "--kb-root",
                    root.as_posix(),
                ],
            }
        }
    }
    return json.dumps(config, indent=2) + "\n"


def inspect_claude_desktop_status(kb_root: Path) -> ClaudeDesktopStatus:
    root = kb_root.expanduser().resolve()
    policy = read_agent_policy(root, "claude-desktop")
    doctor = run_doctor(root)
    ok = doctor.to_dict()["ok"]
    warnings = []
    if policy.read_scope != "wiki_context":
        warnings.append(
            "Claude Desktop practical context is designed for wiki_context; raw sources remain "
            "excluded from practical context tools."
        )
    indexes_root = root / "ai_kb/wiki/indexes"
    if not indexes_root.exists() or not any(indexes_root.glob("*.json")):
        warnings.append("Indexes are missing; run linta index build <kb_root>.")
    return ClaudeDesktopStatus(
        kb_root=root,
        policy_mode=policy.mode,
        read_scope=policy.read_scope,
        kb_ok=ok,
        practical_context_tools=list(PRACTICAL_CONTEXT_TOOLS),
        project_instructions_available=True,
        warnings=warnings,
        message=(
            "Claude Desktop can use the read-only MCP adapter."
            if policy.mode == "read"
            else (
                "Claude Desktop is configured with write mode; "
                "MCP adapter still exposes read tools."
            )
        ),
    )


def claude_desktop_status_json(status: ClaudeDesktopStatus) -> str:
    return json.dumps(status.to_dict(), indent=2) + "\n"


def build_claude_project_instructions(kb_root: Path) -> ClaudeProjectInstructions:
    root = kb_root.expanduser().resolve()
    first_prompt = (
        "Use the Linta MCP server for this project. Start with context_overview, then search or "
        "bundle the compiled wiki context that is relevant to my request."
    )
    instructions = "\n".join(
        [
            "# Linta Project Context",
            "",
            f"Knowledge base root: `{root.as_posix()}`",
            "",
            "Use the Linta MCP server as the project knowledge source. Start each new topic with "
            "`context_overview`, then use `context_search`, `context_read`, and `context_bundle` "
            "to decide which compiled wiki context is relevant.",
            "",
            READ_BOUNDARY,
            "",
            "Prefer `context_bundle` when a query can be answered from multiple wiki pages or "
            "source cards. Prefer `context_read` when a specific Linta path is already known.",
            "",
            "If `context_overview` or `context_bundle` returns freshness warnings, report the "
            "warnings first and ask for the primary writer Agent to run `linta maintenance daily` "
            "or ingest missing sources before relying on stale or incomplete context.",
            "",
            "When answering, cite the Linta paths you used, such as `ai_kb/wiki/current/...`, "
            "`ai_kb/wiki/portfolio/...`, or `ai_kb/wiki/source_cards/...`.",
            "",
            "If the compiled wiki context is insufficient, state the missing context and ask for "
            "the primary writer Agent to ingest or update the knowledge base. Do not bypass Linta "
            "by requesting raw sources.",
            "",
            "Recommended first user prompt:",
            "",
            f"> {first_prompt}",
            "",
        ]
    )
    return ClaudeProjectInstructions(
        kb_root=root,
        instructions=instructions,
        tools=list(PRACTICAL_CONTEXT_TOOLS),
        read_boundary=READ_BOUNDARY,
        recommended_first_prompt=first_prompt,
    )


def claude_project_instructions_json(instructions: ClaudeProjectInstructions) -> str:
    return json.dumps(instructions.to_dict(), indent=2) + "\n"
