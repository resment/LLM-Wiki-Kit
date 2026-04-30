# Daily Maintenance

Run deterministic maintenance. Do not do a full daily re-ingest.

Commands:

```bash
llm-wiki maintenance daily <kb_root>
llm-wiki maintenance daily <kb_root> --json
```

Rules:

- Do not modify `ai_kb/raw/`.
- Do not re-ingest all sources every day.
- Recommend ingest only for new raw sources or explicit inconsistencies.
- Report lint findings and recommended actions.

Output the maintenance report and next recommended action.
