from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_phase3_docs_are_expanded() -> None:
    docs = [
        "docs/philosophy.md",
        "docs/architecture.md",
        "docs/quickstart.md",
        "docs/workflow.md",
        "docs/source-trust-model.md",
        "docs/current-state-workflow.md",
        "docs/mini-kb.md",
        "docs/hermes-deployment.md",
        "docs/codex-workflow.md",
    ]
    for doc in docs:
        text = (REPO_ROOT / doc).read_text(encoding="utf-8")
        assert len(text.splitlines()) >= 10, doc


def test_readmes_are_synchronized_for_current_phase() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_cn = (REPO_ROOT / "README_CN.md").read_text(encoding="utf-8")

    assert "Phase 4" in readme
    assert "Phase 4" in readme_cn
    assert "product-knowledge-ops" in readme
    assert "product-knowledge-ops" in readme_cn


def test_product_knowledge_ops_example_contains_required_relationships() -> None:
    example = REPO_ROOT / "examples/product-knowledge-ops"
    required_files = [
        "ai_kb/raw/meetings/2026-04-21_flexible-review-workflow_meeting.md",
        "ai_kb/raw/weekly/2026-W17_knowledge-portal_weekly.md",
        "ai_kb/raw/docs/2026-04-13_review-model_design.md",
        "ai_kb/wiki/source_manifest.md",
        "ai_kb/wiki/source_cards/meetings__2026-04-21_flexible-review-workflow_meeting.source-card.md",
        "ai_kb/wiki/portfolio/projects.md",
        "ai_kb/wiki/portfolio/capabilities.md",
        "ai_kb/wiki/current/core-knowledge-portal.md",
        "ai_kb/wiki/current_draft/flexible-review-workflow.md",
        "ai_kb/export_for_ai/mini_kb/flexible-review-workflow__review-prep.md",
    ]
    for relative in required_files:
        assert (example / relative).is_file(), relative

    project_text = (example / "ai_kb/wiki/portfolio/projects.md").read_text(encoding="utf-8")
    capability_text = (example / "ai_kb/wiki/portfolio/capabilities.md").read_text(
        encoding="utf-8"
    )
    assert "depends_on Core Knowledge Portal" in project_text
    assert "shares_capability Review Configuration" in project_text
    assert "Flexible Review Workflow" in capability_text
    assert "Team Workflow Expansion" in capability_text


def test_prompt_templates_are_actionable() -> None:
    prompt_dir = REPO_ROOT / "templates/prompts"
    for name in [
        "ingest.md",
        "lint.md",
        "export.md",
        "mini_kb.md",
        "query_writeback.md",
        "confirm_current.md",
    ]:
        text = (prompt_dir / name).read_text(encoding="utf-8")
        assert "Do not" in text or "Rules:" in text
        assert "raw" in text
