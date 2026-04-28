# llm-wiki-kit

`llm-wiki-kit` 是一个 source-available 的 “LLM 编译型 Markdown 知识库” 框架。

它不是普通笔记模板，也不是 RAG 系统。项目把不可变原始资料、AI 编译后的 wiki、人工确认的当前状态，以及面向 AI 工具的导出层分开管理。

## 当前状态

v0.1 Phase 5 提供确定性的项目脚手架、初始化命令、核心本地工具、完善的文档和模板、匿名示例知识库、可选 Hermes skills、发布元数据和示例校验。默认不调用任何 LLM API。

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

Phase 5 支持：

```bash
llm-wiki init ./SimonKnowledgeBase
llm-wiki manifest scan ./SimonKnowledgeBase
llm-wiki source-card create ./SimonKnowledgeBase ai_kb/raw/meetings/example.md
llm-wiki prompt ingest ./SimonKnowledgeBase ai_kb/raw/meetings/example.md
llm-wiki prompt lint-ai ./SimonKnowledgeBase
llm-wiki lint ./SimonKnowledgeBase
llm-wiki export current ./SimonKnowledgeBase
llm-wiki mini-kb create ./SimonKnowledgeBase --topic "Example" --purpose "Review prep"
llm-wiki hermes install-skills --dry-run
python scripts/validate_example.py
```

## current_draft vs current

`current_draft/` 是 AI 生成的当前状态草稿，需要人工审核。`current/` 是人工确认后的正式当前状态。agent 可以更新草稿，但不能在没有明确确认时修改 `current/`。

## 安全边界

- `raw/` 是不可变事实源。
- `current/` 需要人工确认。
- `export_for_ai/` 是消费层，不是事实源。
- 用户应在提交前 review diff。
- 测试不得调用外部 LLM API。

## 许可

llm-wiki-kit 默认采用 PolyForm Noncommercial License 1.0.0。非商业使用可按 `LICENSE`
执行；商业使用必须获得单独的付费商业授权，见 [COMMERCIAL.md](COMMERCIAL.md)。

由于保留商业使用授权权利，本项目不是 OSI 定义下的开源项目，而是 source-available 项目。

## 示例项目

`examples/product-knowledge-ops/` 展示了一个匿名产品知识运营项目组合，包括：

- 多个 raw source；
- source card；
- source manifest；
- 项目页和 capability 页；
- `current/` 与 `current_draft/` 分离；
- 面向评审准备的 mini-kb。

## Hermes adapter

Hermes 集成是可选能力，位于 `hermes/`。安装命令默认复制 skills 到 `~/.hermes/skills/llm-wiki-kit/`，已存在的 skill 默认跳过，除非传入 `--force`。

## 后续路线

见 [ROADMAP.md](ROADMAP.md)。
