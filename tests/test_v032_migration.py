from pathlib import Path

from typer.testing import CliRunner

from linta.agent_access import (
    access_config_path,
    default_agent_access_config,
    legacy_access_config_path,
    render_agent_access_yaml,
)
from linta.cli import app
from linta.doctor import run_doctor
from linta.init_kb import init_knowledge_base
from linta.migration import run_rename_migration

runner = CliRunner()


def test_migrate_copies_legacy_agent_access_policy(tmp_path: Path) -> None:
    root = tmp_path / "kb"
    init_knowledge_base(root)
    legacy_path = legacy_access_config_path(root)
    legacy_path.parent.mkdir(parents=True)
    legacy_path.write_text(
        render_agent_access_yaml(default_agent_access_config("codex")),
        encoding="utf-8",
    )

    report = run_rename_migration(root)

    assert access_config_path(root).read_text(encoding="utf-8") == legacy_path.read_text(
        encoding="utf-8"
    )
    assert any(action.status == "copied" for action in report.actions)


def test_migrate_dry_run_does_not_write(tmp_path: Path) -> None:
    root = tmp_path / "kb"
    init_knowledge_base(root)
    legacy_path = legacy_access_config_path(root)
    legacy_path.parent.mkdir(parents=True)
    legacy_path.write_text(
        render_agent_access_yaml(default_agent_access_config("hermes")),
        encoding="utf-8",
    )

    report = run_rename_migration(root, dry_run=True)

    assert not access_config_path(root).exists()
    assert any(action.status == "would-copy" for action in report.actions)


def test_migrate_replaces_legacy_tag_blocks_in_wiki(tmp_path: Path) -> None:
    root = tmp_path / "kb"
    init_knowledge_base(root)
    page = root / "ai_kb/wiki/projects/example.md"
    page.write_text(
        """# Example

<!-- llm-wiki-tags:start -->
#project/example #status/draft
<!-- llm-wiki-tags:end -->
""",
        encoding="utf-8",
    )

    run_rename_migration(root)

    text = page.read_text(encoding="utf-8")
    assert "<!-- linta-tags:start -->" in text
    assert "<!-- llm-wiki-tags:start -->" not in text
    assert "#project/example #status/draft" in text


def test_doctor_reports_legacy_agent_access(tmp_path: Path) -> None:
    root = tmp_path / "kb"
    init_knowledge_base(root)
    legacy_path = legacy_access_config_path(root)
    legacy_path.parent.mkdir(parents=True)
    legacy_path.write_text(
        render_agent_access_yaml(default_agent_access_config("hermes")),
        encoding="utf-8",
    )

    report = run_doctor(root)

    assert any(check.code == "legacy-agent-access" for check in report.checks)


def test_cli_migrate_json(tmp_path: Path) -> None:
    root = tmp_path / "kb"
    init_knowledge_base(root)

    result = runner.invoke(app, ["migrate", str(root), "--json"])

    assert result.exit_code == 0, result.output
    assert '"actions"' in result.output
