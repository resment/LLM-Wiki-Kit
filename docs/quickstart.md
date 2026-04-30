# Quickstart

```bash
pip install "llm-wiki-kit @ git+https://github.com/resment/LLM-Wiki-Kit.git"
llm-wiki init ./SimonKnowledgeBase
```

For local development after cloning the repository, use:

```bash
pip install -e ".[dev]"
```

Create a raw source:

```bash
mkdir -p SimonKnowledgeBase/ai_kb/raw/meetings
cat > SimonKnowledgeBase/ai_kb/raw/meetings/2026-04-21_example.md <<'EOF'
---
date: 2026-04-21
type: meeting
project: Example Project
---

# Example meeting
EOF
```

Run deterministic tools:

```bash
llm-wiki manifest scan ./SimonKnowledgeBase
llm-wiki source-card create ./SimonKnowledgeBase ai_kb/raw/meetings/2026-04-21_example.md
llm-wiki prompt ingest ./SimonKnowledgeBase ai_kb/raw/meetings/2026-04-21_example.md
llm-wiki tags add ./SimonKnowledgeBase/ai_kb/wiki/source_cards/meetings__2026-04-21_example.source-card.md --tag project/example
llm-wiki index build ./SimonKnowledgeBase
llm-wiki lint ./SimonKnowledgeBase
```

Import an uploaded file:

```bash
llm-wiki raw import ./SimonKnowledgeBase ~/Downloads/uploaded.md --source-type docs
llm-wiki maintenance daily ./SimonKnowledgeBase
```

Export confirmed current pages:

```bash
llm-wiki export current ./SimonKnowledgeBase --single-file current_all.md
```

Create task context:

```bash
llm-wiki mini-kb create ./SimonKnowledgeBase --topic "Example Project" --purpose "Review prep"
```
