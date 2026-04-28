# llm-wiki-kit

`llm-wiki-kit` 是一个 source-available 的 “LLM 编译型 Markdown 知识库” 框架。

它不是普通笔记模板，也不是 RAG 系统。项目把不可变原始资料、AI 编译后的 wiki、人工确认的当前状态，以及面向 AI 工具的导出层分开管理。

## 当前状态

v0.2.2 提供确定性的项目脚手架、初始化命令、manifest 扫描、source card 模板、prompt 渲染、lint、current 导出、mini-kb 草稿、可选 Hermes skills、Obsidian 友好的 Markdown tags、机器可读索引和更强的一致性检查。默认不调用任何 LLM API。

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
ai_kb/wiki/indexes/    机器可读 JSON 索引。
ai_kb/schema/          agent 维护规则。
ai_kb/export_for_ai/   给 ChatGPT / Claude / Gemini 等工具读取的消费层。
archive/               归档资料。
```

## CLI

v0.2.2 支持：

```bash
llm-wiki init ./SimonKnowledgeBase
llm-wiki manifest scan ./SimonKnowledgeBase
llm-wiki manifest scan ./SimonKnowledgeBase --no-preserve-manual-fields
llm-wiki source-card create ./SimonKnowledgeBase ai_kb/raw/meetings/example.md
llm-wiki prompt ingest ./SimonKnowledgeBase ai_kb/raw/meetings/example.md
llm-wiki prompt tag ./SimonKnowledgeBase ai_kb/wiki/projects/example.md
llm-wiki tags list ./SimonKnowledgeBase/ai_kb/wiki/projects/example.md
llm-wiki tags add ./SimonKnowledgeBase/ai_kb/wiki/projects/example.md --tag project/example
llm-wiki tags set ./SimonKnowledgeBase/ai_kb/wiki/projects/example.md --tag status/draft
llm-wiki index build ./SimonKnowledgeBase
llm-wiki prompt lint-ai ./SimonKnowledgeBase
llm-wiki lint ./SimonKnowledgeBase
llm-wiki export current ./SimonKnowledgeBase
llm-wiki mini-kb create ./SimonKnowledgeBase --topic "Example" --purpose "Review prep"
llm-wiki hermes install-skills --dry-run
llm-wiki hermes configure-kb ./SimonKnowledgeBase
python scripts/validate_example.py
```

## Obsidian Tags 与索引

`llm-wiki tags` 会在 wiki Markdown 正文中写入受控 tag block：

```md
<!-- llm-wiki-tags:start -->
#project/example #status/draft #capability/review
<!-- llm-wiki-tags:end -->
```

tag 会规范化为小写 kebab-case，并支持 `#project/...`、`#capability/...`、`#status/...`
等 namespace。CLI 拒绝写入 `ai_kb/raw/`，raw source 仍然保持不可变。`llm-wiki index build`
会在 `ai_kb/wiki/indexes/` 下生成给工具消费的 JSON 索引。

## current_draft vs current

`current_draft/` 是 AI 生成的当前状态草稿，需要人工审核。`current/` 是人工确认后的正式当前状态。agent 可以更新草稿，但不能在没有明确确认时修改 `current/`。

## 安全边界

- `raw/` 是不可变事实源。
- `llm-wiki tags add/set` 拒绝写入 `ai_kb/raw/`。
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

Hermes 集成是可选能力，位于 `hermes/`。安装命令默认复制 skills 到 `~/.hermes/skills/llm-wiki-kit/`，已存在的 skill 默认跳过，除非传入 `--force`。v0.2.1 已包含 Hermes tags/index skills，用于接入现有的 `llm-wiki tags` 和 `llm-wiki index build` 工作流。v0.2.2 增加 `configure-kb`，让 Hermes 通过本地 profile 记住默认知识库路径。

安装 Hermes skills 后，绑定默认知识库：

```bash
llm-wiki hermes configure-kb ./SimonKnowledgeBase
```

该命令会写入 `~/.hermes/skills/llm-wiki-kit/profiles/`。

## 后续路线

见 [ROADMAP.md](ROADMAP.md)。
