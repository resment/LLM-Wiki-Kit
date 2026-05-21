from pathlib import Path

from typer.testing import CliRunner

from linta.cli import app
from linta.indexes import build_indexes
from linta.init_kb import init_knowledge_base
from linta.linting import lint_knowledge_base
from linta.manifest import scan_manifest
from linta.source_card import create_source_card
from linta.tags import (
    TAG_BLOCK_END,
    TAG_BLOCK_START,
    add_tags_to_markdown,
    extract_inline_tags,
    extract_managed_tags,
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


def test_legacy_tag_block_is_read_and_replaced() -> None:
    markdown = """# Example

<!-- llm-wiki-tags:start -->
#project/old
<!-- llm-wiki-tags:end -->
"""

    assert extract_managed_tags(markdown) == ["#project/old"]

    replaced = set_tag_block(markdown, ["project/new"])

    assert "<!-- linta-tags:start -->" in replaced
    assert "<!-- llm-wiki-tags:start -->" not in replaced
    assert "#project/new" in replaced


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


def test_prompt_entities_mentions_entity_workflow(tmp_path: Path) -> None:
    root = make_kb(tmp_path)
    raw = write_raw(root)

    result = runner.invoke(app, ["prompt", "entities", str(root), raw.relative_to(root).as_posix()])

    assert result.exit_code == 0, result.output
    assert "entity context layer" in result.output
    assert "ai_kb/wiki/entities/aliases.md" in result.output
    assert "effective_from" in result.output
    assert "Do not write conclusion-style personal judgments" in result.output


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

<!-- linta-tags:start -->
#project/example #capability/review-configuration
<!-- linta-tags:end -->
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


def test_index_build_outputs_entities_relationships_and_project_map(tmp_path: Path) -> None:
    root = make_kb(tmp_path)
    person = root / "ai_kb/wiki/entities/people/alex-reviewer.md"
    person.write_text(
        """---
title: Alex Reviewer
entity_type: person
entity_id: person.alex-reviewer
aliases: [Alex, A. Reviewer]
relationships:
  - relationship_type: reports_to
    target_entity: team.platform-review
    effective_from: 2026-04-01
    effective_to:
    source_path: ai_kb/raw/meetings/2026-04-21_example.md
---

# Alex Reviewer
""",
        encoding="utf-8",
    )
    team = root / "ai_kb/wiki/entities/teams/platform-review.md"
    team.write_text(
        """---
title: Platform Review
entity_type: team
entity_id: team.platform-review
aliases: [Review Team]
relationships: []
---

# Platform Review
""",
        encoding="utf-8",
    )
    product_line = root / "ai_kb/wiki/entities/product_lines/review-ops.md"
    product_line.write_text(
        """---
title: Review Operations
entity_type: product_line
entity_id: product_line.review-ops
aliases: [Review Ops]
relationships: []
---

# Review Operations
""",
        encoding="utf-8",
    )
    project_map = root / "ai_kb/wiki/portfolio/project_map.md"
    project_map.write_text(
        """---
title: Project Map
projects:
  - project: Review Routing
    aliases: [Routing Project]
    related_people: [person.alex-reviewer]
    related_teams: [team.platform-review]
    current_phase: beta
    possible_blockers: [policy review]
    historical_controversy_points: [routing scope]
    sources: [ai_kb/raw/meetings/2026-04-21_example.md]
---

# Project Map
""",
        encoding="utf-8",
    )

    result = build_indexes(root)

    assert (root / "ai_kb/wiki/indexes/entities.json").exists()
    assert (root / "ai_kb/wiki/indexes/relationships.json").exists()
    assert (root / "ai_kb/wiki/indexes/project_map.json").exists()
    assert result.data["entities"][0]["entity_id"] == "person.alex-reviewer"
    assert result.data["entities"][0]["aliases"] == ["Alex", "A. Reviewer"]
    assert result.data["relationships"][0]["relationship_type"] == "reports_to"
    assert result.data["relationships"][0]["source_path"].endswith("2026-04-21_example.md")
    assert result.data["project_map"][0]["project"] == "Review Routing"
    assert result.data["project_map"][0]["related_people"] == ["person.alex-reviewer"]


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

<!-- linta-tags:start -->
#Bad_Tag #bad-tag
<!-- linta-tags:end -->

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


def test_lint_detects_entity_context_issues(tmp_path: Path) -> None:
    root = make_kb(tmp_path)
    first = root / "ai_kb/wiki/entities/people/alex.md"
    first.write_text(
        """---
title: Alex
entity_type: person
entity_id: person.alex
aliases: [Alex]
relationships:
  - relationship_type: reports_to
    target_entity: team.review
---

# Alex

## Personality
""",
        encoding="utf-8",
    )
    second = root / "ai_kb/wiki/entities/people/alex-other.md"
    second.write_text(
        """---
title: Alex Other
entity_type: person
entity_id: person.alex-other
aliases: [Alex]
relationships: []
---

# Alex Other
""",
        encoding="utf-8",
    )
    current = root / "ai_kb/wiki/current/entity-summary.md"
    current.write_text(
        """---
title: Entity Summary
---

# Entity Summary

## Observed Concerns

Concern without source citation.
""",
        encoding="utf-8",
    )

    issues = lint_knowledge_base(root)
    codes = {issue.code for issue in issues}

    assert "duplicate-entity-alias" in codes
    assert "relationship-missing-source-path" in codes
    assert "forbidden-entity-judgment" in codes
    assert "entity-observation-missing-source-citation" in codes


def test_cli_index_build(tmp_path: Path) -> None:
    root = make_kb(tmp_path)

    result = runner.invoke(app, ["index", "build", str(root), "--dry-run"])

    assert result.exit_code == 0, result.output
    assert "Would build" in result.output
    assert "sources" in result.output
