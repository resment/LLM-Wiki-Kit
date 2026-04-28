from pathlib import Path

from typer.testing import CliRunner

from llm_wiki_kit.cli import app
from llm_wiki_kit.indexes import build_indexes
from llm_wiki_kit.init_kb import init_knowledge_base
from llm_wiki_kit.linting import lint_knowledge_base
from llm_wiki_kit.manifest import scan_manifest
from llm_wiki_kit.source_card import create_source_card
from llm_wiki_kit.tags import (
    TAG_BLOCK_END,
    TAG_BLOCK_START,
    add_tags_to_markdown,
    extract_inline_tags,
    normalize_tag,
    set_tag_block,
)

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

# Example
""",
        encoding="utf-8",
    )
    return raw


def test_normalize_and_extract_inline_tags() -> None:
    assert normalize_tag("Project/Core Knowledge Portal") == "#project/core-knowledge-portal"
    assert normalize_tag("#Status/Draft") == "#status/draft"
    assert extract_inline_tags("#status/draft text #Project/Core_Knowledge") == [
        "#status/draft",
        "#project/core-knowledge",
    ]


def test_tag_block_insert_and_replace_after_frontmatter() -> None:
    markdown = "---\ntitle: Example\n---\n\n# Example\nbody #user/tag\n"

    updated = add_tags_to_markdown(markdown, ["Project/Core", "#status/draft", "project/core"])
    assert updated.index("---\ntitle: Example\n---") < updated.index(TAG_BLOCK_START)
    assert updated.index(TAG_BLOCK_START) < updated.index("# Example")
    assert "#project/core #status/draft" in updated
    assert updated.count("#project/core") == 1
    assert "#user/tag" in updated

    replaced = set_tag_block(updated, ["capability/Review"])
    assert "#capability/review" in replaced
    assert "#status/draft" not in replaced
    assert TAG_BLOCK_END in replaced
    assert "#user/tag" in replaced


def test_cli_tags_add_set_list_and_raw_write_rejected(tmp_path: Path) -> None:
    root = make_kb(tmp_path)
    page = root / "ai_kb/wiki/projects/example.md"
    page.write_text("---\ntitle: Example\n---\n\n# Example\n", encoding="utf-8")

    missing_tag_result = runner.invoke(app, ["tags", "add", str(page)])
    assert missing_tag_result.exit_code == 2

    add_result = runner.invoke(
        app,
        ["tags", "add", str(page), "--tag", "Project/Example", "--tag", "status/Draft"],
    )
    assert add_result.exit_code == 0, add_result.output

    list_result = runner.invoke(app, ["tags", "list", str(page)])
    assert list_result.exit_code == 0, list_result.output
    assert "#project/example" in list_result.output
    assert "#status/draft" in list_result.output

    set_result = runner.invoke(app, ["tags", "set", str(page), "--tag", "capability/review"])
    assert set_result.exit_code == 0, set_result.output
    assert "#capability/review" in page.read_text(encoding="utf-8")

    before_dry_run = page.read_text(encoding="utf-8")
    dry_run_result = runner.invoke(
        app,
        ["tags", "add", str(page), "--tag", "status/final", "--dry-run"],
    )
    assert dry_run_result.exit_code == 0, dry_run_result.output
    assert "#status/final" in dry_run_result.output
    assert page.read_text(encoding="utf-8") == before_dry_run

    raw = write_raw(root)
    raw_result = runner.invoke(app, ["tags", "add", str(raw), "--tag", "raw"])
    assert raw_result.exit_code == 1
    assert "immutable raw" in raw_result.output


def test_prompt_tag_mentions_obsidian_and_raw_rule(tmp_path: Path) -> None:
    root = make_kb(tmp_path)
    page = root / "ai_kb/wiki/projects/example.md"
    page.write_text("---\ntitle: Example\n---\n\n# Example\n", encoding="utf-8")

    result = runner.invoke(app, ["prompt", "tag", str(root), "ai_kb/wiki/projects/example.md"])

    assert result.exit_code == 0, result.output
    assert "Obsidian inline tags" in result.output
    assert "Do not modify" in result.output
    assert "#project/..." in result.output


def test_manifest_scan_preserves_manual_fields(tmp_path: Path) -> None:
    root = make_kb(tmp_path)
    write_raw(root)
    manifest = root / "ai_kb/wiki/source_manifest.md"
    manifest.write_text(
        """---
title: Source Manifest
---

# Source Manifest

| Source path | Date | Type | Project | Ingest status | Source card | Last updated |
| --- | --- | --- | --- | --- | --- | --- |
| ai_kb/raw/meetings/2026-04-21_example.md | old | old | Manual Project | reviewed | missing | old |
""",
        encoding="utf-8",
    )

    preserved = scan_manifest(root)
    rebuilt = scan_manifest(root, preserve_manual_fields=False, dry_run=True)

    assert "Manual Project" in preserved
    assert "reviewed" in preserved
    assert "Example Project" in rebuilt
    assert "reviewed" not in rebuilt


def test_index_build_outputs_sources_projects_capabilities_and_tags(tmp_path: Path) -> None:
    root = make_kb(tmp_path)
    raw = write_raw(root)
    create_source_card(root, raw.relative_to(root))
    project = root / "ai_kb/wiki/projects/example.md"
    project.write_text(
        """---
title: Example
project: Example Project
capabilities: [Review Configuration]
---

<!-- llm-wiki-tags:start -->
#project/example #capability/review-configuration
<!-- llm-wiki-tags:end -->
""",
        encoding="utf-8",
    )

    result = build_indexes(root)

    assert (root / "ai_kb/wiki/indexes/sources.json").exists()
    assert (root / "ai_kb/wiki/indexes/projects.json").exists()
    assert (root / "ai_kb/wiki/indexes/capabilities.json").exists()
    assert (root / "ai_kb/wiki/indexes/tags.json").exists()
    assert result.data["sources"][0]["source_path"].endswith("2026-04-21_example.md")
    assert result.data["projects"][0]["name"] == "Example Project"
    assert result.data["capabilities"][0]["name"] == "Review Configuration"
    assert result.data["tags"][0]["tag"] == "#capability/review-configuration"


def test_index_build_dry_run_does_not_write(tmp_path: Path) -> None:
    root = make_kb(tmp_path)

    result = build_indexes(root, dry_run=True)

    assert result.dry_run is True
    assert not (root / "ai_kb/wiki/indexes/sources.json").exists()
    assert result.data["sources"] == []


def test_lint_detects_links_source_card_current_citations_and_tags(tmp_path: Path) -> None:
    root = make_kb(tmp_path)
    card = root / "ai_kb/wiki/source_cards/bad.source-card.md"
    card.write_text(
        """---
source_path: ai_kb/raw/missing.md
source_type: meeting
---

# Bad Card
""",
        encoding="utf-8",
    )
    current = root / "ai_kb/wiki/current/example.md"
    current.write_text(
        """---
title: Current
---

<!-- llm-wiki-tags:start -->
#Bad_Tag #bad-tag
<!-- llm-wiki-tags:end -->

[Missing](../missing.md)
""",
        encoding="utf-8",
    )

    issues = lint_knowledge_base(root)
    codes = {issue.code for issue in issues}

    assert "source-card-missing-field" in codes
    assert "source-card-source-missing" in codes
    assert "missing-source-citation" in codes
    assert "broken-markdown-link" in codes
    assert "invalid-managed-tag" in codes


def test_cli_index_build(tmp_path: Path) -> None:
    root = make_kb(tmp_path)

    result = runner.invoke(app, ["index", "build", str(root), "--dry-run"])

    assert result.exit_code == 0, result.output
    assert "Would build" in result.output
    assert "sources" in result.output
