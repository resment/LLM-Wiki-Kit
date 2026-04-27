# llm-wiki-kit

`llm-wiki-kit` 是一个用于构建 “LLM 编译型 Markdown 知识库” 的框架。

它不是普通笔记模板，也不是 RAG 系统。项目把不可变原始资料、AI 编译后的 wiki、人工确认的当前状态，以及面向 AI 工具的导出层分开管理。

## 当前状态

v0.1 Phase 2 提供确定性的项目脚手架、初始化命令和核心本地工具。默认不调用任何 LLM API。

## 快速开始

```bash
pip install -e ".[dev]"
llm-wiki init ./SimonKnowledgeBase
```

## 核心目录

```text
human/                 用户本人写作区，AI 默认不编辑。
ai_kb/raw/             不可变事实源。
ai_kb/wiki/            AI 编译后的知识层。
ai_kb/schema/          agent 维护规则。
ai_kb/export_for_ai/   给 ChatGPT / Claude / Gemini 等工具读取的消费层。
archive/               归档资料。
```

## CLI

Phase 2 支持：

```bash
llm-wiki init ./SimonKnowledgeBase
llm-wiki manifest scan ./SimonKnowledgeBase
llm-wiki source-card create ./SimonKnowledgeBase ai_kb/raw/meetings/example.md
llm-wiki prompt ingest ./SimonKnowledgeBase ai_kb/raw/meetings/example.md
llm-wiki prompt lint-ai ./SimonKnowledgeBase
llm-wiki lint ./SimonKnowledgeBase
llm-wiki export current ./SimonKnowledgeBase
llm-wiki mini-kb create ./SimonKnowledgeBase --topic "Example" --purpose "Review prep"
```

## current_draft vs current

`current_draft/` 是 AI 生成的当前状态草稿，需要人工审核。`current/` 是人工确认后的正式当前状态。agent 可以更新草稿，但不能在没有明确确认时修改 `current/`。

## 安全边界

- `raw/` 是不可变事实源。
- `current/` 需要人工确认。
- `export_for_ai/` 是消费层，不是事实源。
- 用户应在提交前 review diff。
- 测试不得调用外部 LLM API。

## 后续路线

- Phase 3：完善模板、文档和匿名示例。
- Phase 4：可选 Hermes adapter。
- Phase 5：打磨、校验和发布准备。
