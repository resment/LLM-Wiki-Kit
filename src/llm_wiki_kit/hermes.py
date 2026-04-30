"""Optional Hermes skill installation."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from importlib.resources import files
from pathlib import Path

DEFAULT_HERMES_SKILL_TARGET = Path.home() / ".hermes/skills/llm-wiki-kit"
DEFAULT_HERMES_PROFILE = "default"


@dataclass
class HermesInstallResult:
    """Result of a Hermes skill installation run."""

    target: Path
    dry_run: bool
    copied: list[Path] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)


@dataclass(frozen=True)
class HermesProfileResult:
    """Result of writing a Hermes knowledge-base profile."""

    path: Path
    content: str
    dry_run: bool


def install_skills(
    *,
    target: Path | None = None,
    dry_run: bool = False,
    force: bool = False,
) -> HermesInstallResult:
    """Install bundled Hermes skills into a target directory."""

    source_root = hermes_skills_root()
    destination_root = (target or DEFAULT_HERMES_SKILL_TARGET).expanduser().resolve()
    result = HermesInstallResult(target=destination_root, dry_run=dry_run)

    for source_skill in sorted(path for path in source_root.iterdir() if path.is_dir()):
        destination_skill = destination_root / source_skill.name
        if destination_skill.exists() and not force:
            result.skipped.append(destination_skill)
            continue
        result.copied.append(destination_skill)
        if dry_run:
            continue
        destination_root.mkdir(parents=True, exist_ok=True)
        if destination_skill.exists():
            shutil.rmtree(destination_skill)
        shutil.copytree(source_skill, destination_skill)

    return result


def configure_knowledge_base_profile(
    kb_root: Path,
    *,
    target: Path | None = None,
    profile: str = DEFAULT_HERMES_PROFILE,
    dry_run: bool = False,
    force: bool = False,
) -> HermesProfileResult:
    """Write a Hermes profile that points at a knowledge-base root."""

    root = kb_root.expanduser().resolve()
    _validate_kb_root(root)
    destination_root = (target or DEFAULT_HERMES_SKILL_TARGET).expanduser().resolve()
    profile_path = destination_root / "profiles" / f"{_normalize_profile_name(profile)}.md"
    if profile_path.exists() and not force:
        raise FileExistsError(f"Hermes profile already exists: {profile_path}")
    content = render_hermes_profile(root, profile=profile)
    if not dry_run:
        profile_path.parent.mkdir(parents=True, exist_ok=True)
        profile_path.write_text(content, encoding="utf-8")
    return HermesProfileResult(path=profile_path, content=content, dry_run=dry_run)


def render_hermes_profile(kb_root: Path, *, profile: str = DEFAULT_HERMES_PROFILE) -> str:
    root = kb_root.expanduser().resolve()
    return f"""# llm-wiki-kit Hermes Profile: {profile}

Knowledge base root:

```text
{root}
```

Use this knowledge base root when the user asks Hermes to maintain the default llm-wiki-kit
knowledge base.

## Default Commands

```bash
llm-wiki manifest scan {root}
llm-wiki lint {root}
llm-wiki index build {root}
llm-wiki maintenance daily {root}
```

## Upload Handling

When the user asks Hermes to process an uploaded file, import it first:

```bash
llm-wiki raw import {root} <uploaded-file> --source-type docs
```

Then create a source card and use the ingest workflow only for the imported raw source.

## Safety Rules

- Do not edit, delete, rename, summarize-in-place, or move files under `ai_kb/raw/`.
- Write proposed current-state changes to `ai_kb/wiki/current_draft/`.
- Do not update `ai_kb/wiki/current/` unless the user explicitly confirms.
- Treat `ai_kb/wiki/indexes/` and `ai_kb/export_for_ai/` as derived outputs.
- Do daily maintenance checks instead of daily full re-ingest.
- Cite source paths for important claims.
"""


def render_bootstrap_prompt(
    kb_root: Path,
    *,
    target: Path | None = None,
    profile: str = DEFAULT_HERMES_PROFILE,
) -> str:
    """Render a natural-language prompt for Hermes Agent first-use installation."""

    root = kb_root.expanduser().resolve()
    target_root = (target or DEFAULT_HERMES_SKILL_TARGET).expanduser().resolve()
    normalized_profile = _normalize_profile_name(profile)
    return f"""请帮我安装并配置 llm-wiki-kit 的 Hermes 接入。

目标知识库路径：

```text
{root}
```

Hermes skills 目标目录：

```text
{target_root}
```

Profile 名称：

```text
{normalized_profile}
```

请按顺序执行：

```bash
llm-wiki hermes install-skills --target "{target_root}"
llm-wiki hermes configure-kb "{root}" --target "{target_root}" --profile "{normalized_profile}"
llm-wiki lint "{root}"
llm-wiki maintenance daily "{root}" --dry-run
```

如果 profile 已存在，请先停下来告诉我，不要自动覆盖；只有我明确确认后才使用 `--force`。

安装完成后，请告诉我：

- 已安装或跳过的 skills；
- profile 文件路径；
- `llm-wiki lint` 的结果；
- 后续我可以如何要求你维护这个知识库。
- 如何处理“刚上传的文件”。

安全边界：

- 不要修改 `ai_kb/raw/`。
- 默认只写 `ai_kb/wiki/current_draft/`，不要直接写 `ai_kb/wiki/current/`。
- `ai_kb/wiki/indexes/` 和 `ai_kb/export_for_ai/` 是派生输出。
- 每日维护只运行 deterministic maintenance，不要每日全量 re-ingest。
- 如果用户要求处理刚上传的文件，先用 `llm-wiki raw import` 导入 raw，再只对该 source 准备 ingest。
- 重要结论必须引用 source path。
"""


def hermes_skills_root() -> Path:
    """Return bundled Hermes skills from source checkout or installed package data."""

    repo_skills = Path(__file__).resolve().parents[2] / "hermes/skills"
    if repo_skills.exists():
        return repo_skills
    return Path(str(files("llm_wiki_kit") / "assets/hermes/skills"))


def _validate_kb_root(root: Path) -> None:
    if not root.exists():
        raise FileNotFoundError(f"Knowledge base root does not exist: {root}")
    required = [
        root / "AGENTS.md",
        root / "ai_kb/schema/AGENTS.md",
        root / "ai_kb/wiki/source_manifest.md",
    ]
    missing = [path.relative_to(root).as_posix() for path in required if not path.exists()]
    if missing:
        raise ValueError(f"Not an llm-wiki-kit knowledge base; missing: {', '.join(missing)}")


def _normalize_profile_name(profile: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_.-]+", "-", profile.strip().lower()).strip("-")
    if not normalized:
        raise ValueError("Profile name must not be empty.")
    return normalized
