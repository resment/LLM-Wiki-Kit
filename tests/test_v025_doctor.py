from pathlib import Path

from typer.testing import CliRunner

from llm_wiki_kit.cli import app
from llm_wiki_kit.doctor import doctor_json, run_doctor
from llm_wiki_kit.init_kb import init_knowledge_base

runner = CliRunner()


def test_doctor_reports_initialized_kb(tmp_path: Path) -> None:
    root = tmp_path / "kb"
    init_knowledge_base(root)

    report = run_doctor(root)
    codes = {check.code for check in report.checks}

    assert report.version
    assert "version" in codes
    assert "path-ok" in codes
    assert not any(check.severity == "error" for check in report.checks)


def test_doctor_reports_missing_required_files(tmp_path: Path) -> None:
    root = tmp_path / "kb"
    root.mkdir()

    report = run_doctor(root)

    assert any(check.severity == "error" for check in report.checks)
    assert any(check.path == "AGENTS.md" for check in report.checks)


def test_doctor_json_and_cli_do_not_write(tmp_path: Path) -> None:
    root = tmp_path / "kb"
    init_knowledge_base(root)
    before = sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))

    report = run_doctor(root)
    payload = doctor_json(report)
    cli_result = runner.invoke(app, ["doctor", str(root), "--json"])
    after = sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))

    assert '"ok": true' in payload
    assert cli_result.exit_code == 0, cli_result.output
    assert '"checks"' in cli_result.output
    assert before == after
