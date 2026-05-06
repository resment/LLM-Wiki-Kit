"""Agent access policy configuration for llm-wiki-kit knowledge bases."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

AGENT_ACCESS_RELATIVE_PATH = ".llm-wiki/agent_access.yaml"

AGENTS = ("hermes", "codex", "openclaw", "claude_desktop")
AGENT_ALIASES = {
    "hermes": "hermes",
    "codex": "codex",
    "openclaw": "openclaw",
    "claude": "claude_desktop",
    "claude-desktop": "claude_desktop",
    "claude_desktop": "claude_desktop",
}
MODES = ("read", "write")
READ_SCOPES = ("exports_only", "wiki_context", "full_kb")
READ_SCOPE_ALIASES = {
    "exports-only": "exports_only",
    "exports_only": "exports_only",
    "wiki-context": "wiki_context",
    "wiki_context": "wiki_context",
    "full-kb": "full_kb",
    "full_kb": "full_kb",
}

WIKI_CONTEXT_PATHS = (
    "README.md",
    "AGENTS.md",
    "ai_kb/schema/AGENTS.md",
    "ai_kb/wiki/current",
    "ai_kb/wiki/portfolio",
    "ai_kb/wiki/indexes",
    "ai_kb/wiki/source_manifest.md",
    "ai_kb/wiki/source_cards",
)
EXPORTS_ONLY_PATHS = (
    "README.md",
    "ai_kb/export_for_ai",
    "ai_kb/wiki/indexes",
)


@dataclass(frozen=True)
class AgentPolicy:
    mode: str
    read_scope: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class AgentAccessConfig:
    version: int
    primary_agent: str
    agents: dict[str, AgentPolicy]

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "primary_agent": self.primary_agent,
            "agents": {name: policy.to_dict() for name, policy in self.agents.items()},
        }


@dataclass(frozen=True)
class AgentAccessResult:
    path: Path
    config: AgentAccessConfig
    dry_run: bool


def access_config_path(kb_root: Path) -> Path:
    return kb_root.expanduser().resolve() / AGENT_ACCESS_RELATIVE_PATH


def normalize_agent(agent: str) -> str:
    key = agent.strip().lower().replace(" ", "-")
    normalized = AGENT_ALIASES.get(key)
    if not normalized:
        raise ValueError(f"Unknown agent: {agent}")
    return normalized


def normalize_mode(mode: str) -> str:
    normalized = mode.strip().lower().replace(" ", "-")
    if normalized not in MODES:
        raise ValueError(f"Mode must be one of: {', '.join(MODES)}")
    return normalized


def normalize_read_scope(read_scope: str) -> str:
    key = read_scope.strip().lower().replace(" ", "-")
    normalized = READ_SCOPE_ALIASES.get(key)
    if not normalized:
        raise ValueError(f"Read scope must be one of: {', '.join(READ_SCOPES)}")
    return normalized


def default_agent_access_config(primary_agent: str) -> AgentAccessConfig:
    primary = normalize_agent(primary_agent)
    agents = {
        agent: AgentPolicy(
            mode="write" if agent == primary else "read",
            read_scope="full_kb" if agent == primary else "wiki_context",
        )
        for agent in AGENTS
    }
    return AgentAccessConfig(version=1, primary_agent=primary, agents=agents)


def write_agent_access_config(
    kb_root: Path,
    config: AgentAccessConfig,
    *,
    dry_run: bool = False,
    force: bool = False,
) -> AgentAccessResult:
    root = kb_root.expanduser().resolve()
    _validate_kb_root(root)
    path = access_config_path(root)
    if path.exists() and not force:
        raise FileExistsError(f"Agent access config already exists: {path}")
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_agent_access_yaml(config), encoding="utf-8")
    return AgentAccessResult(path=path, config=config, dry_run=dry_run)


def configure_agent_access(
    kb_root: Path,
    *,
    primary_agent: str,
    dry_run: bool = False,
    force: bool = False,
) -> AgentAccessResult:
    return write_agent_access_config(
        kb_root,
        default_agent_access_config(primary_agent),
        dry_run=dry_run,
        force=force,
    )


def set_agent_access(
    kb_root: Path,
    *,
    agent: str,
    mode: str,
    read_scope: str,
    dry_run: bool = False,
) -> AgentAccessResult:
    root = kb_root.expanduser().resolve()
    config = read_agent_access_config(root)
    normalized_agent = normalize_agent(agent)
    policy = AgentPolicy(mode=normalize_mode(mode), read_scope=normalize_read_scope(read_scope))
    agents = dict(config.agents)
    agents[normalized_agent] = policy
    primary_agent = config.primary_agent
    if policy.mode == "write":
        primary_agent = normalized_agent
        agents = {
            name: (value if name == normalized_agent else AgentPolicy("read", value.read_scope))
            for name, value in agents.items()
        }
    elif normalized_agent == primary_agent:
        replacement = _first_writer(agents)
        if replacement is None:
            raise ValueError("At least one agent must remain in write mode.")
        primary_agent = replacement
    result = AgentAccessConfig(version=config.version, primary_agent=primary_agent, agents=agents)
    path = access_config_path(root)
    if not dry_run:
        path.write_text(render_agent_access_yaml(result), encoding="utf-8")
    return AgentAccessResult(path=path, config=result, dry_run=dry_run)


def read_agent_access_config(kb_root: Path) -> AgentAccessConfig:
    path = access_config_path(kb_root)
    if not path.exists():
        raise FileNotFoundError(f"Agent access config does not exist: {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return parse_agent_access(raw)


def read_agent_policy(kb_root: Path, agent: str) -> AgentPolicy:
    config = read_agent_access_config(kb_root)
    normalized = normalize_agent(agent)
    return config.agents[normalized]


def parse_agent_access(raw: dict[str, Any]) -> AgentAccessConfig:
    version = int(raw.get("version") or 1)
    primary_agent = normalize_agent(str(raw.get("primary_agent") or "hermes"))
    raw_agents = raw.get("agents") or {}
    agents: dict[str, AgentPolicy] = {}
    for agent in AGENTS:
        raw_policy = raw_agents.get(agent) or {}
        default_policy = AgentPolicy(
            mode="write" if agent == primary_agent else "read",
            read_scope="full_kb" if agent == primary_agent else "wiki_context",
        )
        agents[agent] = AgentPolicy(
            mode=normalize_mode(str(raw_policy.get("mode") or default_policy.mode)),
            read_scope=normalize_read_scope(
                str(raw_policy.get("read_scope") or default_policy.read_scope)
            ),
        )
    writers = [name for name, policy in agents.items() if policy.mode == "write"]
    if primary_agent not in writers:
        agents[primary_agent] = AgentPolicy("write", agents[primary_agent].read_scope)
    for writer in writers:
        if writer != primary_agent:
            agents[writer] = AgentPolicy("read", agents[writer].read_scope)
    return AgentAccessConfig(version=version, primary_agent=primary_agent, agents=agents)


def render_agent_access_yaml(config: AgentAccessConfig) -> str:
    return yaml.safe_dump(config.to_dict(), sort_keys=False, allow_unicode=False)


def agent_access_json(config: AgentAccessConfig) -> str:
    return json.dumps(config.to_dict(), indent=2) + "\n"


def agent_access_markdown(config: AgentAccessConfig, path: Path) -> str:
    lines = [
        "# llm-wiki-kit Agent Access",
        "",
        f"- Config: `{path}`",
        f"- Version: `{config.version}`",
        f"- Primary agent: `{config.primary_agent}`",
        "",
        "| Agent | Mode | Read scope |",
        "| --- | --- | --- |",
    ]
    for agent in AGENTS:
        policy = config.agents[agent]
        lines.append(f"| `{agent}` | `{policy.mode}` | `{policy.read_scope}` |")
    return "\n".join(lines) + "\n"


def allowed_read_roots(kb_root: Path, policy: AgentPolicy) -> list[Path]:
    root = kb_root.expanduser().resolve()
    if policy.read_scope == "full_kb":
        return [root]
    relatives = EXPORTS_ONLY_PATHS if policy.read_scope == "exports_only" else WIKI_CONTEXT_PATHS
    return [(root / relative).resolve() for relative in relatives]


def is_read_allowed(kb_root: Path, policy: AgentPolicy, path: Path) -> bool:
    root = kb_root.expanduser().resolve()
    target = path.expanduser().resolve()
    if not _is_relative_to(target, root):
        return False
    if target == access_config_path(root):
        return False
    return any(
        target == allowed or _is_relative_to(target, allowed)
        for allowed in allowed_read_roots(root, policy)
    )


def list_allowed_context_files(kb_root: Path, policy: AgentPolicy) -> list[str]:
    root = kb_root.expanduser().resolve()
    files: set[str] = set()
    for allowed in allowed_read_roots(root, policy):
        if allowed.is_file():
            files.add(allowed.relative_to(root).as_posix())
        elif allowed.is_dir():
            for path in allowed.rglob("*"):
                if path.is_file() and is_read_allowed(root, policy, path):
                    files.add(path.relative_to(root).as_posix())
    return sorted(files)


def _validate_kb_root(root: Path) -> None:
    required = (
        root / "AGENTS.md",
        root / "ai_kb/schema/AGENTS.md",
        root / "ai_kb/wiki/source_manifest.md",
    )
    missing = [path.relative_to(root).as_posix() for path in required if not path.exists()]
    if missing:
        raise ValueError(f"Not an llm-wiki-kit knowledge base; missing: {', '.join(missing)}")


def _first_writer(agents: dict[str, AgentPolicy]) -> str | None:
    for agent, policy in agents.items():
        if policy.mode == "write":
            return agent
    return None


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True
