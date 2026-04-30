from pathlib import Path

from typer.testing import CliRunner

from llm_wiki_kit.cli import app
from llm_wiki_kit.init_kb import init_knowledge_base
from llm_wiki_kit.maintenance import maintenance_json, run_daily_maintenance
from llm_wiki_kit.raw_import import import_raw_source
from llm_wiki_kit.source_card import create_source_card

runner = CliRunner()


def make_kb(tmp_path: Path) -> Path:
    root = tmp_path / "kb"
    init_knowledge_base(root)
    return root


def test_raw_import_copies_to_source_type(tmp_path: Path) -> None:
    root = make_kb(tmp_path)
    uploaded = tmp_path / "Upload File.md"
    uploaded.write_text("# Uploaded", encoding="utf-8")

    result = import_raw_source(root, uploaded, source_type="docs")

    assert result.relative_destination == "ai_kb/raw/docs/Upload-File.md"
    assert (root / result.relative_destination).read_text(encoding="utf-8") == "# Uploaded"


def test_raw_import_dry_run_and_force(tmp_path: Path) -> None:
    root = make_kb(tmp_path)
    uploaded = tmp_path / "source.md"
    uploaded.write_text("first", encoding="utf-8")

    dry_run = import_raw_source(root, uploaded, source_type="meetings", dry_run=True)
    assert dry_run.dry_run is True
    assert not (root / dry_run.relative_destination).exists()

    import_raw_source(root, uploaded, source_type="meetings")
    uploaded.write_text("second", encoding="utf-8")
    result = runner.invoke(
        app,
        ["raw", "import", str(root), str(uploaded), "--source-type", "meetings"],
    )
    assert result.exit_code == 1
    assert "already exists" in result.output

    forced = runner.invoke(
        app,
        ["raw", "import", str(root), str(uploaded), "--source-type", "meetings", "--force"],
    )
    assert forced.exit_code == 0, forced.output
    assert (root / "ai_kb/raw/meetings/source.md").read_text(encoding="utf-8") == "second"


def test_raw_import_invalid_source_type_exits_config_error(tmp_path: Path) -> None:
    root = make_kb(tmp_path)
    uploaded = tmp_path / "source.md"
    uploaded.write_text("content", encoding="utf-8")

    result = runner.invoke(
        app,
        ["raw", "import", str(root), str(uploaded), "--source-type", "assets"],
    )

    assert result.exit_code == 2
    assert "--source-type must be one of" in result.output


def test_daily_maintenance_reports_new_raw_and_missing_source_card(tmp_path: Path) -> None:
    root = make_kb(tmp_path)
    raw = root / "ai_kb/raw/docs/2026-04-30_uploaded.md"
    raw.write_text("# Uploaded", encoding="utf-8")

    report = run_daily_maintenance(root, dry_run=True)

    assert "ai_kb/raw/docs/2026-04-30_uploaded.md" in report.new_raw_sources
    assert "ai_kb/raw/docs/2026-04-30_uploaded.md" in report.missing_source_cards
    assert any("ingest new raw source" in action for action in report.recommended_actions)


def test_daily_maintenance_clean_kb_reports_no_ingest_needed(tmp_path: Path) -> None:
    root = make_kb(tmp_path)
    raw = root / "ai_kb/raw/docs/2026-04-30_uploaded.md"
    raw.write_text("# Uploaded", encoding="utf-8")
    create_source_card(root, raw.relative_to(root))
    run_daily_maintenance(root)

    report = run_daily_maintenance(root, dry_run=True)

    assert report.new_raw_sources == []
    assert report.missing_source_cards == []
    assert "No ingest needed" in report.recommended_actions[0]


def test_daily_maintenance_json_and_cli(tmp_path: Path) -> None:
    root = make_kb(tmp_path)

    report = run_daily_maintenance(root, dry_run=True)
    assert '"new_raw_sources": []' in maintenance_json(report)

    cli_result = runner.invoke(app, ["maintenance", "daily", str(root), "--json", "--dry-run"])
    assert cli_result.exit_code == 0, cli_result.output
    assert '"recommended_actions"' in cli_result.output
