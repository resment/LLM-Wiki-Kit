"""Prompt rendering helpers."""

from __future__ import annotations

from pathlib import Path

from llm_wiki_kit.source_card import source_card_path


def render_prompt(kb_root: Path, template_name: str, values: dict[str, str]) -> str:
    """Render a named prompt template from templates/prompts."""

    template = _template_root() / "prompts" / f"{template_name}.md"
    text = template.read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def render_ingest_prompt(kb_root: Path, raw_source: Path) -> str:
    root = kb_root.expanduser().resolve()
    source = raw_source if raw_source.is_absolute() else root / raw_source
    relative_source = source.resolve().relative_to(root).as_posix()
    card_path = source_card_path(root, relative_source).relative_to(root).as_posix()
    return render_prompt(
        root,
        "ingest",
        {
            "kb_root": root.as_posix(),
            "source_path": relative_source,
            "agents_path": "ai_kb/schema/AGENTS.md",
            "source_manifest_path": "ai_kb/wiki/source_manifest.md",
            "source_card_path": card_path,
        },
    )


def render_lint_ai_prompt(kb_root: Path) -> str:
    root = kb_root.expanduser().resolve()
    return render_prompt(root, "lint", {"kb_root": root.as_posix()})


def _template_root() -> Path:
    return Path(__file__).resolve().parents[2] / "templates"
