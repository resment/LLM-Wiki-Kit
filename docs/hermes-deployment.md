# Hermes Deployment

Hermes integration is optional. Phase 3 documents the intended deployment shape; installation
automation is planned for Phase 4.

Expected layout:

```text
hermes/
├─ README.md
├─ skills/
│  ├─ ingest_raw_source/
│  ├─ lint_knowledge_base/
│  ├─ generate_mini_kb/
│  ├─ export_for_ai/
│  └─ confirm_current/
└─ install_skills.sh
```

Hermes skills should follow the same safety boundaries as the CLI:

- never mutate `ai_kb/raw/`;
- write `current_draft/` by default;
- write `current/` only in an explicit confirmation skill;
- cite source paths;
- output human review questions.
