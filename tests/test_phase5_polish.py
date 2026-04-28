import os
import subprocess
import sys
from pathlib import Path
from tomllib import loads

from scripts.validate_example import validate_example

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_project_metadata_is_release_ready() -> None:
    metadata = loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = metadata["project"]

    assert project["name"] == "llm-wiki-kit"
    assert project["version"] == "0.2.3"
    assert project["requires-python"] == ">=3.11"
    assert project["license"]["text"] == "PolyForm-Noncommercial-1.0.0"
    assert "llm-wiki" in project["scripts"]
    assert "Homepage" in project["urls"]
    assert all("OSI Approved" not in classifier for classifier in project["classifiers"])


def test_manifest_includes_public_assets() -> None:
    manifest = (REPO_ROOT / "MANIFEST.in").read_text(encoding="utf-8")
    metadata = loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    setuptools_config = metadata["tool"]["setuptools"]
    data_files = metadata["tool"]["setuptools"]["data-files"]

    assert "README_CN.md" in manifest
    assert "COMMERCIAL.md" in manifest
    assert "CONTRIBUTING.md" in manifest
    assert "recursive-include docs *.md" in manifest
    assert "recursive-include templates *.md" in manifest
    assert "recursive-include hermes *.md *.sh" in manifest
    assert "recursive-include examples *.md" in manifest
    assert "assets/hermes/skills/*/*.md" in setuptools_config["package-data"]["llm_wiki_kit"]
    assert (REPO_ROOT / "src/llm_wiki_kit/assets/hermes/skills/build_indexes/SKILL.md").is_file()
    assert (
        REPO_ROOT / "src/llm_wiki_kit/assets/hermes/skills/manage_obsidian_tags/SKILL.md"
    ).is_file()
    assert "templates/prompts/tag.md" in data_files["templates/prompts"]
    assert "COMMERCIAL.md" in setuptools_config["license-files"]
    assert "CONTRIBUTING.md" in setuptools_config["license-files"]


def test_license_files_reserve_commercial_rights() -> None:
    license_text = (REPO_ROOT / "LICENSE").read_text(encoding="utf-8")
    commercial = (REPO_ROOT / "COMMERCIAL.md").read_text(encoding="utf-8")
    contributing = (REPO_ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")

    assert "PolyForm Noncommercial License 1.0.0" in license_text
    assert "Required Notice: Copyright 2026 llm-wiki-kit contributors" in license_text
    assert "Commercial use requires a separate written" in commercial
    assert "separate commercial licenses" in contributing


def test_readmes_and_roadmap_are_v02_current() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_cn = (REPO_ROOT / "README_CN.md").read_text(encoding="utf-8")
    roadmap = (REPO_ROOT / "ROADMAP.md").read_text(encoding="utf-8")

    assert "v0.2.3" in readme
    assert "v0.2.3" in readme_cn
    assert "Obsidian" in readme
    assert "Obsidian" in readme_cn
    assert "Hermes tags/index" in readme
    assert "Hermes tags/index" in readme_cn
    assert "configure-kb" in readme
    assert "configure-kb" in readme_cn
    assert "bootstrap-prompt" in readme
    assert "bootstrap-prompt" in readme_cn
    assert "v0.2.3 Status" in roadmap
    assert "v0.2.2 Status" in roadmap
    assert "v0.2.1 Status" in roadmap
    assert "v0.2 Status" in roadmap
    assert "Phase 5" in roadmap
    assert "No built-in LLM API calls" in roadmap


def test_product_knowledge_ops_example_validates() -> None:
    errors = validate_example(REPO_ROOT / "examples/product-knowledge-ops")

    assert errors == []


def test_module_entrypoint_help() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    result = subprocess.run(
        [sys.executable, "-m", "llm_wiki_kit", "--help"],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Usage:" in result.stdout
    assert "hermes" in result.stdout
