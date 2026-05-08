# 灵台 Linta

`Linta`，中文名「灵台」，是一个 source-available 的 “LLM 编译型 Markdown 知识库” 框架。

它不是普通笔记模板，也不是 RAG 系统。项目把不可变原始资料、AI 编译后的 wiki、人工确认的当前状态，以及面向 AI 工具的导出层分开管理。

## 当前状态

v0.3.3 提供确定性的项目脚手架、初始化命令、manifest 扫描、source card 模板、prompt 渲染、lint、current 导出、mini-kb 草稿、可选 Hermes skills、Obsidian 友好的 Markdown tags、机器可读索引、上传文档导入、每日维护报告、doctor、Hermes status、多 Agent 访问策略和带 practical context tools 的 Claude Desktop 只读 MCP adapter。默认不调用任何 LLM API。

## 快速开始

```bash
pip install "linta @ git+https://github.com/resment/Linta.git"
linta init ./SimonKnowledgeBase
```

如果是 clone 仓库后的本地开发环境，再使用 `pip install -e ".[dev]"`。

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

v0.3.3 支持：

```bash
linta init ./SimonKnowledgeBase
linta manifest scan ./SimonKnowledgeBase
linta manifest scan ./SimonKnowledgeBase --no-preserve-manual-fields
linta source-card create ./SimonKnowledgeBase ai_kb/raw/meetings/example.md
linta prompt ingest ./SimonKnowledgeBase ai_kb/raw/meetings/example.md
linta prompt tag ./SimonKnowledgeBase ai_kb/wiki/projects/example.md
linta tags list ./SimonKnowledgeBase/ai_kb/wiki/projects/example.md
linta tags add ./SimonKnowledgeBase/ai_kb/wiki/projects/example.md --tag project/example
linta tags set ./SimonKnowledgeBase/ai_kb/wiki/projects/example.md --tag status/draft
linta index build ./SimonKnowledgeBase
linta raw import ./SimonKnowledgeBase ~/Downloads/uploaded.md --source-type docs
linta maintenance daily ./SimonKnowledgeBase
linta doctor ./SimonKnowledgeBase
linta migrate ./SimonKnowledgeBase --dry-run
linta agents wizard ./SimonKnowledgeBase
linta agents status ./SimonKnowledgeBase
linta claude-desktop config ./SimonKnowledgeBase
linta claude-desktop status ./SimonKnowledgeBase
linta mcp serve --agent claude-desktop --kb-root ./SimonKnowledgeBase
linta prompt lint-ai ./SimonKnowledgeBase
linta lint ./SimonKnowledgeBase
linta export current ./SimonKnowledgeBase
linta mini-kb create ./SimonKnowledgeBase --topic "Example" --purpose "Review prep"
linta hermes install-skills --dry-run
linta hermes status
linta hermes bootstrap-prompt ./SimonKnowledgeBase
linta hermes configure-kb ./SimonKnowledgeBase
python scripts/validate_example.py
```

## 安装后验证

初始化或配置 Hermes 后运行：

```bash
linta doctor ./SimonKnowledgeBase
linta agents wizard ./SimonKnowledgeBase
linta hermes status
```

`doctor` 检查知识库结构和确定性健康状态。`hermes status` 检查 skills、profiles 和默认知识库路径是否有效。

## 改名迁移

从旧名称升级到 Linta 后运行：

```bash
linta migrate ./SimonKnowledgeBase --dry-run
linta migrate ./SimonKnowledgeBase
```

迁移会在需要时把旧 `.llm-wiki/agent_access.yaml` 复制到 `.linta/agent_access.yaml`，把旧 `llm-wiki-tags` block 替换为 `linta-tags`，并报告旧 Hermes skills 目录。

## 多 Agent 访问策略

默认使用一个主读写 Agent，其他 Agent 只读：

```bash
linta agents wizard ./SimonKnowledgeBase
linta agents status ./SimonKnowledgeBase
```

策略写入知识库内部的 `.linta/agent_access.yaml`。常见配置是 Hermes 或 Codex 作为写入者，Claude Desktop 和 OpenClaw 只读。Claude Desktop 默认使用 `wiki_context`，可读取 confirmed/current wiki context、source cards、manifest、portfolio pages 和 indexes，但不读取 raw sources、current drafts、human notes 或 archive。

Claude Desktop 接入：

```bash
linta claude-desktop config ./SimonKnowledgeBase
linta claude-desktop status ./SimonKnowledgeBase
```

把生成的 MCP 片段加入 Claude Desktop 配置后重启应用。只读边界只适用于 Linta 提供的 MCP adapter；如果额外给 Claude Desktop 配置了 filesystem 或 shell 写权限，那些外部工具不受本项目强制约束。

Claude Desktop 推荐先调用 `context_overview`，再用 `context_search`、`context_read` 和
`context_bundle` 自行选择相关的已整理 wiki 上下文。这些 practical context tools 不读取
`ai_kb/raw/`；raw 仍然是主写入 Agent 使用的原始物料层。

## Obsidian Tags 与索引

`linta tags` 会在 wiki Markdown 正文中写入受控 tag block：

```md
<!-- linta-tags:start -->
#project/example #status/draft #capability/review
<!-- linta-tags:end -->
```

tag 会规范化为小写 kebab-case，并支持 `#project/...`、`#capability/...`、`#status/...`
等 namespace。CLI 拒绝写入 `ai_kb/raw/`，raw source 仍然保持不可变。`linta index build`
会在 `ai_kb/wiki/indexes/` 下生成给工具消费的 JSON 索引。

## 上传与每日维护

Hermes gateway 或聊天入口上传的文件，应先导入 raw：

```bash
linta raw import ./SimonKnowledgeBase ~/Downloads/uploaded.md --source-type docs
```

每日维护不应该全量重新 ingest。运行：

```bash
linta maintenance daily ./SimonKnowledgeBase
```

报告会列出新增 raw source、缺失 source card、lint 问题和建议动作。需要 LLM 判断、总结、编译 wiki 的步骤由用户已配置好的 Agent 执行，例如 Hermes。

## current_draft vs current

`current_draft/` 是 AI 生成的当前状态草稿，需要人工审核。`current/` 是人工确认后的正式当前状态。agent 可以更新草稿，但不能在没有明确确认时修改 `current/`。

## 安全边界

- `raw/` 是不可变事实源。
- `linta tags add/set` 拒绝写入 `ai_kb/raw/`。
- `current/` 需要人工确认。
- `export_for_ai/` 是消费层，不是事实源。
- 用户应在提交前 review diff。
- 测试不得调用外部 LLM API。

## 许可

Linta 默认采用 PolyForm Noncommercial License 1.0.0。非商业使用可按 `LICENSE`
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

Hermes 集成是可选能力，位于 `hermes/`。安装命令默认复制 skills 到 `~/.hermes/skills/linta/`，已存在的 skill 默认跳过，除非传入 `--force`。v0.2.1 已包含 Hermes tags/index skills，用于接入现有的 `linta tags` 和 `linta index build` 工作流。v0.2.2 增加 `configure-kb`，让 Hermes 通过本地 profile 记住默认知识库路径。v0.2.3 增加 `bootstrap-prompt`，可生成直接粘贴给 Hermes Agent 的自然语言安装请求。v0.2.4 增加上传导入和每日维护 skills。

安装 Hermes skills 后，绑定默认知识库：

```bash
linta hermes bootstrap-prompt ./SimonKnowledgeBase
linta hermes configure-kb ./SimonKnowledgeBase
```

`bootstrap-prompt` 会输出给 Hermes Agent 执行的自然语言步骤；`configure-kb` 会写入 `~/.hermes/skills/linta/profiles/`。

## 后续路线

见 [ROADMAP.md](ROADMAP.md)。
