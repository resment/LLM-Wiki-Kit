"""Claude Desktop configuration helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from llm_wiki_kit.agent_access import read_agent_policy
from llm_wiki_kit.doctor import run_doctor


@dataclass(frozen=True)
class ClaudeDesktopStatus:
    kb_root: Path
    policy_mode: str
    read_scope: str
    kb_ok: bool
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "kb_root": self.kb_root.as_posix(),
            "policy_mode": self.policy_mode,
            "read_scope": self.read_scope,
            "kb_ok": self.kb_ok,
            "message": self.message,
        }


def render_claude_desktop_config(kb_root: Path) -> str:
    root = kb_root.expanduser().resolve()
    config = {
        "mcpServers": {
            "llm-wiki-kit": {
                "command": "llm-wiki",
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
    return ClaudeDesktopStatus(
        kb_root=root,
        policy_mode=policy.mode,
        read_scope=policy.read_scope,
        kb_ok=ok,
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
