import os
from pathlib import Path
from time import time

from typer.testing import CliRunner

from llm_wiki_kit.cli import app
from llm_wiki_kit.export import export_current
from llm_wiki_kit.init_kb import init_knowledge_base
from llm_wiki_kit.linting import lint_knowledge_base
from llm_wiki_kit.manifest import scan_manifest
from llm_wiki_kit.mini_kb import create_mini_kb
from llm_wiki_kit.prompts import render_ingest_prompt
from llm_wiki_kit.source_card import create_source_card, source_card_path

runner = CliRunner()


def make_kb(tmp_path: Path) -> Path:
    root = tmp_path / "kb"
    init_knowledge_base(root)
    return root


def write_raw(root: Path) -> Path:
    raw = root / "ai_kb/raw/meetings/2026-04-21_example.md"
    raw.write_text(
        """---
date: 2026-04-21
type: meeting
project: Example Project
---

# Meeting
""",
        encoding="utf-8",
    )
    return raw


def test_manifest_scan_updates_markdown(tmp_path: Path) -> None:
    root = make_kb(tmp_path)
    write_raw(root)

    content = scan_manifest(root)

    assert "ai_kb/raw/meetings/2026-04-21_example.md" in content
    assert "Example Project" in content
    manifest = root / "ai_kb/wiki/source_manifest.md"
    assert "2026-04-21" in manifest.read_text(encoding="utf-8")


def test_source_card_path_and_create(tmp_path: Path) -> None:
    root = make_kb(tmp_path)
    raw = write_raw(root)

    result = create_source_card(root, raw.relative_to(root))

    assert result.path == source_card_path(root, "ai_kb/raw/meetings/2026-04-21_example.md")
    text = result.path.read_text(encoding="utf-8")
    assert "source_path: ai_kb/raw/meetings/2026-04-21_example.md" in text
    assert "source_type: meeting" in text


def test_source_card_create_allows_missing_raw_path(tmp_path: Path) -> None:
    root = make_kb(tmp_path)

    result = create_source_card(root, Path("ai_kb/raw/meetings/example.md"))

    assert result.path.exists()
    assert "source_path: ai_kb/raw/meetings/example.md" in result.content


def test_prompt_ingest_renders_paths(tmp_path: Path) -> None:
    root = make_kb(tmp_path)

    prompt = render_ingest_prompt(root, Path("ai_kb/raw/meetings/example.md"))

    assert "ai_kb/raw/meetings/example.md" in prompt
    assert "ai_kb/schema/AGENTS.md" in prompt
    assert "Do not modify" in prompt
    assert "current_draft only" in prompt


def test_lint_missing_manifest_entry_and_source_card(tmp_path: Path) -> None:
    root = make_kb(tmp_path)
    write_raw(root)

    issues = lint_knowledge_base(root)

    codes = {issue.code for issue in issues}
    assert "raw-not-in-manifest" in codes
    assert "missing-source-card" in codes


def test_lint_stale_current_and_old_export(tmp_path: Path) -> None:
    root = make_kb(tmp_path)
    current = root / "ai_kb/wiki/current/example.md"
    exported = root / "ai_kb/export_for_ai/current/example.md"
    current.write_text("---\ntitle: Example\n---\n\n# Example\n", encoding="utf-8")
    exported.write_text("# Old export\n", encoding="utf-8")
    old_time = time() - 3 * 24 * 60 * 60
    exported_time = time() - 4 * 24 * 60 * 60
    current.touch()
    exported.touch()
    os.utime(current, (old_time, old_time))
    os.utime(exported, (exported_time, exported_time))

    issues = lint_knowledge_base(root, max_current_age=1)

    codes = {issue.code for issue in issues}
    assert "stale-current" in codes
    assert "export-older-than-current" in codes


def test_export_current(tmp_path: Path) -> None:
    root = make_kb(tmp_path)
    current = root / "ai_kb/wiki/current/example.md"
    current.write_text("---\ntitle: Example\n---\n\n# Example\n", encoding="utf-8")

    result = export_current(root, single_file="current_all.md")

    assert root / "ai_kb/export_for_ai/current/example.md" in result.files
    assert (root / "ai_kb/export_for_ai/current/example.md").exists()
    assert (root / "ai_kb/export_for_ai/current/current_all.md").exists()


def test_mini_kb_create(tmp_path: Path) -> None:
    root = make_kb(tmp_path)

    result = create_mini_kb(root, topic="Example Project", purpose="Review prep")

    assert result.path.name == "example-project__review-prep.md"
    assert "MiniKB: Example Project / Review prep" in result.content
    assert result.path.exists()


def test_cli_phase2_commands(tmp_path: Path) -> None:
    root = make_kb(tmp_path)
    write_raw(root)

    manifest_result = runner.invoke(app, ["manifest", "scan", str(root)])
    assert manifest_result.exit_code == 0, manifest_result.output

    card_result = runner.invoke(
        app,
        ["source-card", "create", str(root), "ai_kb/raw/meetings/2026-04-21_example.md"],
    )
    assert card_result.exit_code == 0, card_result.output

    prompt_result = runner.invoke(
        app,
        ["prompt", "ingest", str(root), "ai_kb/raw/meetings/2026-04-21_example.md"],
    )
    assert prompt_result.exit_code == 0, prompt_result.output
    assert "ai_kb/wiki/source_cards" in prompt_result.output

    mini_result = runner.invoke(
        app,
        ["mini-kb", "create", str(root), "--topic", "Example", "--purpose", "Review"],
    )
    assert mini_result.exit_code == 0, mini_result.output

    export_result = runner.invoke(app, ["export", "current", str(root)])
    assert export_result.exit_code == 0, export_result.output
