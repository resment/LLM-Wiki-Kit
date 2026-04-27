from pathlib import Path

from typer.testing import CliRunner

from llm_wiki_kit.cli import app
from llm_wiki_kit.hermes import install_skills

runner = CliRunner()

EXPECTED_SKILLS = {
    "ingest_raw_source",
    "lint_knowledge_base",
    "generate_mini_kb",
    "export_for_ai",
    "confirm_current",
}


def test_hermes_install_dry_run_does_not_write(tmp_path: Path) -> None:
    target = tmp_path / "skills"

    result = install_skills(target=target, dry_run=True)

    assert {path.name for path in result.copied} == EXPECTED_SKILLS
    assert not target.exists()


def test_hermes_install_copies_skills(tmp_path: Path) -> None:
    target = tmp_path / "skills"

    result = install_skills(target=target)

    assert {path.name for path in result.copied} == EXPECTED_SKILLS
    for skill in EXPECTED_SKILLS:
        assert (target / skill / "SKILL.md").is_file()
        assert (target / skill / "prompt.md").is_file()


def test_hermes_install_skips_existing_without_force(tmp_path: Path) -> None:
    target = tmp_path / "skills"
    existing = target / "ingest_raw_source"
    existing.mkdir(parents=True)
    marker = existing / "SKILL.md"
    marker.write_text("custom", encoding="utf-8")

    result = install_skills(target=target)

    assert existing in result.skipped
    assert marker.read_text(encoding="utf-8") == "custom"


def test_hermes_install_force_overwrites_existing(tmp_path: Path) -> None:
    target = tmp_path / "skills"
    existing = target / "ingest_raw_source"
    existing.mkdir(parents=True)
    marker = existing / "SKILL.md"
    marker.write_text("custom", encoding="utf-8")

    install_skills(target=target, force=True)

    assert "ingest_raw_source" in marker.read_text(encoding="utf-8")


def test_cli_hermes_install_dry_run(tmp_path: Path) -> None:
    target = tmp_path / "skills"

    result = runner.invoke(app, ["hermes", "install-skills", "--target", str(target), "--dry-run"])

    assert result.exit_code == 0, result.output
    assert "Would install" in result.output
    assert "ingest_raw_source" in result.output
    assert not target.exists()


def test_hermes_skill_docs_have_required_sections() -> None:
    root = Path(__file__).resolve().parents[1]
    for skill in EXPECTED_SKILLS:
        text = (root / "hermes/skills" / skill / "SKILL.md").read_text(encoding="utf-8")
        assert "## Purpose" in text
        assert "## When to Use" in text
        assert "## Inputs" in text
        assert "## Steps" in text
        assert "## Safety Rules" in text
        assert "## Outputs" in text
        assert "## Files It May Edit" in text
        assert "## Files It Must Not Edit" in text
