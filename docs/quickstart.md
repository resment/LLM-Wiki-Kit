# Quickstart

```bash
pip install -e ".[dev]"
llm-wiki init ./SimonKnowledgeBase
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
llm-wiki lint ./SimonKnowledgeBase
```

Export confirmed current pages:

```bash
llm-wiki export current ./SimonKnowledgeBase --single-file current_all.md
```

Create task context:

```bash
llm-wiki mini-kb create ./SimonKnowledgeBase --topic "Example Project" --purpose "Review prep"
```
