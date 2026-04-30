from pathlib import Path

from typer.testing import CliRunner

from llm_wiki_kit.cli import app
from llm_wiki_kit.hermes import (
    configure_knowledge_base_profile,
    inspect_hermes_status,
    install_skills,
    render_bootstrap_prompt,
)
from llm_wiki_kit.init_kb import init_knowledge_base

runner = CliRunner()

EXPECTED_SKILLS = {
    "build_indexes",
    "confirm_current",
    "daily_maintenance",
    "export_for_ai",
    "generate_mini_kb",
    "import_uploaded_raw_source",
    "ingest_raw_source",
    "lint_knowledge_base",
    "manage_obsidian_tags",
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
    assert "configure-kb" in result.output
    assert not target.exists()


def test_hermes_configure_kb_writes_default_profile(tmp_path: Path) -> None:
    kb_root = tmp_path / "kb"
    target = tmp_path / "skills"
    init_knowledge_base(kb_root)

    result = configure_knowledge_base_profile(kb_root, target=target)

    assert result.path == target / "profiles/default.md"
    assert result.path.is_file()
    assert str(kb_root.resolve()) in result.content
    assert "ai_kb/raw/" in result.content


def test_hermes_configure_kb_dry_run_does_not_write(tmp_path: Path) -> None:
    kb_root = tmp_path / "kb"
    target = tmp_path / "skills"
    init_knowledge_base(kb_root)

    result = configure_knowledge_base_profile(kb_root, target=target, dry_run=True)

    assert result.dry_run is True
    assert not result.path.exists()
    assert str(kb_root.resolve()) in result.content


def test_hermes_configure_kb_requires_force_for_existing_profile(tmp_path: Path) -> None:
    kb_root = tmp_path / "kb"
    target = tmp_path / "skills"
    init_knowledge_base(kb_root)
    configure_knowledge_base_profile(kb_root, target=target)

    result = runner.invoke(app, ["hermes", "configure-kb", str(kb_root), "--target", str(target)])

    assert result.exit_code == 1
    assert "already exists" in result.output

    force_result = runner.invoke(
        app,
        ["hermes", "configure-kb", str(kb_root), "--target", str(target), "--force"],
    )
    assert force_result.exit_code == 0, force_result.output
    assert "Wrote" in force_result.output


def test_hermes_bootstrap_prompt_includes_install_configure_and_safety(tmp_path: Path) -> None:
    kb_root = tmp_path / "kb"
    init_knowledge_base(kb_root)

    prompt = render_bootstrap_prompt(kb_root, target=tmp_path / "skills", profile="Work KB")

    assert "llm-wiki hermes install-skills" in prompt
    assert "llm-wiki hermes configure-kb" in prompt
    assert "llm-wiki lint" in prompt
    assert "llm-wiki maintenance daily" in prompt
    assert "llm-wiki raw import" in prompt
    assert str(kb_root.resolve()) in prompt
    assert "work-kb" in prompt
    assert "ai_kb/raw/" in prompt


def test_cli_hermes_bootstrap_prompt(tmp_path: Path) -> None:
    kb_root = tmp_path / "kb"
    init_knowledge_base(kb_root)

    result = runner.invoke(app, ["hermes", "bootstrap-prompt", str(kb_root)])

    assert result.exit_code == 0, result.output
    assert "请帮我安装并配置" in result.output
    assert "llm-wiki hermes install-skills" in result.output
    assert str(kb_root.resolve()) in result.output


def test_hermes_status_reports_missing_install(tmp_path: Path) -> None:
    target = tmp_path / "missing-skills"

    status = inspect_hermes_status(target=target)

    assert status.installed is False
    assert "ingest_raw_source" in status.missing_skills
    assert status.profiles == []


def test_hermes_status_reports_skills_and_valid_profile(tmp_path: Path) -> None:
    target = tmp_path / "skills"
    kb_root = tmp_path / "kb"
    init_knowledge_base(kb_root)
    install_skills(target=target)
    configure_knowledge_base_profile(kb_root, target=target)

    status = inspect_hermes_status(target=target)

    assert status.installed is True
    assert "ingest_raw_source" in status.installed_skills
    assert status.missing_skills == []
    assert status.profiles[0].name == "default"
    assert status.profiles[0].valid is True


def test_hermes_status_reports_invalid_profile(tmp_path: Path) -> None:
    target = tmp_path / "skills"
    profile_root = target / "profiles"
    profile_root.mkdir(parents=True)
    (profile_root / "default.md").write_text(
        """# Profile

Knowledge base root:

```text
/tmp/does-not-exist
```
""",
        encoding="utf-8",
    )

    status = inspect_hermes_status(target=target)

    assert status.profiles[0].valid is False
    assert "invalid" in status.profiles[0].message


def test_cli_hermes_status(tmp_path: Path) -> None:
    target = tmp_path / "skills"

    result = runner.invoke(app, ["hermes", "status", "--target", str(target)])

    assert result.exit_code == 0, result.output
    assert "Installed: False" in result.output
    assert "ingest_raw_source" in result.output


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
