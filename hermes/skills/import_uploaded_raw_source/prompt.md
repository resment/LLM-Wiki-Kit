# Import Uploaded Raw Source

Use this workflow when the user asks you to process a newly uploaded file.

Commands:

```bash
llm-wiki raw import <kb_root> <uploaded_file> --source-type docs
llm-wiki manifest scan <kb_root>
llm-wiki source-card create <kb_root> <imported_raw_path>
llm-wiki index build <kb_root>
llm-wiki lint <kb_root>
```

Rules:

- Do not modify existing files under `ai_kb/raw/`.
- Do not overwrite raw files unless the user explicitly confirms.
- Do not do a full re-ingest.
- Use the ingest workflow only for the imported raw source.

Output imported path, changed files, lint findings, and review questions.
