import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_codex_plugin_manifest_and_skill_are_complete() -> None:
    manifest_path = REPO_ROOT / "plugins/linta/.codex-plugin/plugin.json"
    skill_path = REPO_ROOT / "plugins/linta/skills/linta/SKILL.md"
    marketplace_path = REPO_ROOT / ".agents/plugins/marketplace.json"

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    skill = skill_path.read_text(encoding="utf-8")

    assert manifest["name"] == "linta"
    assert manifest["skills"] == "./skills/"
    assert "[TODO:" not in manifest_path.read_text(encoding="utf-8")
    assert "Do not mutate files under `ai_kb/raw/`" in skill
    assert marketplace["plugins"][0]["name"] == "linta"
    assert marketplace["plugins"][0]["source"]["path"] == "./plugins/linta"


def test_committed_plugin_docs_do_not_include_private_values() -> None:
    paths = [
        REPO_ROOT / "plugins/linta/.codex-plugin/plugin.json",
        REPO_ROOT / "plugins/linta/README.md",
        REPO_ROOT / "plugins/linta/skills/linta/SKILL.md",
        REPO_ROOT / ".agents/plugins/marketplace.json",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)

    assert "linta-ai" not in combined.lower()
    assert "/Users/" not in combined
    assert "127.0.0.1" not in combined
    assert "replace-with-private" not in combined
