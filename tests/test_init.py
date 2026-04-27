from pathlib import Path

import pytest
from typer.testing import CliRunner

from llm_wiki_kit.cli import app
from llm_wiki_kit.init_kb import InitError, init_knowledge_base

runner = CliRunner()


CORE_DIRECTORIES = [
    "human/inbox",
    "human/notes",
    "human/drafts",
    "ai_kb/raw/meetings",
    "ai_kb/raw/weekly",
    "ai_kb/raw/docs",
    "ai_kb/raw/chats",
    "ai_kb/raw/web_clips",
    "ai_kb/raw/data",
    "ai_kb/raw/assets",
    "ai_kb/wiki/source_cards",
    "ai_kb/wiki/portfolio",
    "ai_kb/wiki/projects",
    "ai_kb/wiki/domains",
    "ai_kb/wiki/capabilities",
    "ai_kb/wiki/concepts",
    "ai_kb/wiki/analysis",
    "ai_kb/wiki/current",
    "ai_kb/wiki/current_draft",
    "ai_kb/schema",
    "ai_kb/export_for_ai/current",
    "ai_kb/export_for_ai/mini_kb",
    "ai_kb/export_for_ai/recent",
    "ai_kb/scripts",
    "archive",
]

CORE_FILES = [
    "README.md",
    "AGENTS.md",
    "ai_kb/schema/AGENTS.md",
    "ai_kb/wiki/index.md",
    "ai_kb/wiki/log.md",
    "ai_kb/wiki/source_manifest.md",
    "ai_kb/wiki/portfolio/projects.md",
    "ai_kb/wiki/portfolio/capabilities.md",
    "ai_kb/wiki/portfolio/source_trust.md",
]


def assert_core_layout(root: Path) -> None:
    for directory in CORE_DIRECTORIES:
        assert (root / directory).is_dir(), directory
    for file_path in CORE_FILES:
        assert (root / file_path).is_file(), file_path


def test_init_empty_directory(tmp_path: Path) -> None:
    target = tmp_path / "kb"

    result = init_knowledge_base(target)

    assert result.root == target.resolve()
    assert_core_layout(target)


def test_init_existing_non_empty_directory_fails(tmp_path: Path) -> None:
    target = tmp_path / "kb"
    target.mkdir()
    (target / "notes.md").write_text("existing", encoding="utf-8")

    with pytest.raises(InitError, match="not empty"):
        init_knowledge_base(target)


def test_init_dry_run_does_not_create_files(tmp_path: Path) -> None:
    target = tmp_path / "dry-run-kb"

    result = init_knowledge_base(target, dry_run=True)

    assert result.dry_run is True
    assert not target.exists()
    assert result.plan.files


def test_init_force_writes_into_existing_directory(tmp_path: Path) -> None:
    target = tmp_path / "kb"
    target.mkdir()
    existing = target / "keep.md"
    existing.write_text("keep", encoding="utf-8")

    init_knowledge_base(target, force=True)

    assert existing.read_text(encoding="utf-8") == "keep"
    assert_core_layout(target)


def test_cli_init(tmp_path: Path) -> None:
    target = tmp_path / "kb"

    result = runner.invoke(app, ["init", str(target)])

    assert result.exit_code == 0, result.output
    assert "Initialized" in result.output
    assert_core_layout(target)


def test_cli_init_dry_run(tmp_path: Path) -> None:
    target = tmp_path / "kb"

    result = runner.invoke(app, ["init", str(target), "--dry-run"])

    assert result.exit_code == 0, result.output
    assert "Would initialize" in result.output
    assert not target.exists()


def test_cli_init_existing_non_empty_directory_fails(tmp_path: Path) -> None:
    target = tmp_path / "kb"
    target.mkdir()
    (target / "notes.md").write_text("existing", encoding="utf-8")

    result = runner.invoke(app, ["init", str(target)])

    assert result.exit_code == 1
    assert "Use --force" in result.output
