# 灵台 Linta

<p align="center">
  <img src="assets/linta-promo-cn-01-4k.jpg" alt="灵台：让 AI 读懂你的知识库" width="100%">
</p>

<p align="center">
  <img src="assets/linta-promo-cn-02-4k.jpg" alt="灵台知识库断点和整理流程" width="49%">
  <img src="assets/linta-promo-cn-03-4k.jpg" alt="灵台给 AI 的知识编译层" width="49%">
</p>
<p align="center">
  <img src="assets/linta-promo-cn-04-4k.jpg" alt="灵台知识库的两种整理方式" width="49%">
</p>

`Linta`，中文名「灵台」，可以把零散笔记、会议实录、文档和 AI 对话整理成一个让后续 AI
真正读得懂的知识库。

很多个人或团队知识库会慢慢变成 AI 很难使用的资料堆：原始文件越积越多，人名和项目名不断变化，旧语境和当前事实混在一起，每次新对话又要重新解释背景。Linta 提供的是一层基于 Markdown、来源引用和人工 review 的 AI 记忆整理层。

## 为什么用 Linta

- 原始材料保持不可变，会议纪要、文档和聊天记录不会被 AI 改写污染。
- AI 可以把混乱材料编译成清晰的 wiki、source card、项目地图和当前状态摘要。
- ChatGPT、Claude、Gemini、Hermes、Codex 等工具可以读取整理后的上下文，而不是每次塞一堆 raw 文件。
- 可以维护人、团队、别名、产品线和项目关系，让模型知道“谁和什么有关”。
- 可以区分历史语境和当前事实，避免旧角色、旧结论覆盖今天的情况。

## 安装、升级、删除

对大多数用户来说，Linta 就是一个很小的本地命令行工具。安装一次之后，可以在 Codex、Hermes、Terminal，或任何能执行本地命令的 agent 里使用。

| 目标 | 命令 | 会发生什么 |
| --- | --- | --- |
| 安装 Linta | `pip install "linta @ git+https://github.com/resment/Linta.git"` | 在当前 Python 环境里加入 `linta` 命令。 |
| 升级到最新版本 | `pip install --upgrade "linta @ git+https://github.com/resment/Linta.git"` | 用 GitHub 上的最新版替换本地已安装版本。 |
| 查看当前版本 | `linta --version` | 输出当前安装的 Linta 版本。 |
| 删除 Linta | `pip uninstall linta` | 删除 Python 包和命令；已经创建的知识库文件夹会保留在磁盘上。 |
| 参与源码开发 | `pip install -e ".[dev]"` | 把 clone 下来的源码以可编辑开发模式安装。 |

如果你的 Python 环境不允许全局安装，可以先创建虚拟环境，或者把 Linta 安装到你的 agent 工具正在使用的 Python 环境里。

## 你可以怎么说

下面是可以直接对 Codex、Hermes 或其他 agent 说的自然语言，以及背后对应的 Linta 命令。

| 你可以这样说 | 背后的命令 | 能实现什么 |
| --- | --- | --- |
| “在这里创建一个 AI 能读懂的知识库。” | `linta init ./MyKnowledgeBase` | 创建标准目录和初始维护规则。 |
| “把这个上传的文档放进知识库。” | `linta raw import ./MyKnowledgeBase ~/Downloads/file.md --source-type docs` | 把文件导入不可变 raw 区。 |
| “帮我把这份会议纪要准备成可整理的材料。” | `linta source-card create ./MyKnowledgeBase ai_kb/raw/meetings/example.md` | 为单个 raw 文件生成 source card。 |
| “读取这份材料，更新相关 wiki。” | `linta prompt ingest ./MyKnowledgeBase ai_kb/raw/meetings/example.md` | 给 agent 一套明确的 ingest 工作流。 |
| “从这份材料里提取人、团队、别名和项目关系。” | `linta prompt entities ./MyKnowledgeBase ai_kb/raw/meetings/example.md` | 专门更新实体、别名和项目映射。 |
| “给这个项目评审整理一个小上下文包。” | `linta mini-kb create ./MyKnowledgeBase --topic "Project" --purpose "Review prep"` | 生成面向单次任务的小知识库。 |
| “检查一下这个知识库有没有问题。” | `linta doctor ./MyKnowledgeBase` | 检查目录、必需文件和安装状态。 |
| “看看最近有什么需要维护。” | `linta maintenance daily ./MyKnowledgeBase` | 找出新增 raw、缺失 source card 和 lint 问题。 |
| “让 Claude Desktop 能只读访问这个知识库。” | `linta claude-desktop config ./MyKnowledgeBase` | 输出本地 Claude Desktop MCP 配置片段。 |
| “把这个知识库作为 Claude 远程 Connector 暴露出去。” | `linta mcp serve-http --kb-root ./MyKnowledgeBase` | 启动带 bearer token 的远程 MCP endpoint。 |
| “导出已经确认的当前知识给其他 AI 工具用。” | `linta export current ./MyKnowledgeBase` | 把审核过的 current 内容复制到导出层。 |

## 快速开始

```bash
pip install "linta @ git+https://github.com/resment/Linta.git"
linta init ./MyKnowledgeBase
```

然后把文件放进 `ai_kb/raw/`，用 `linta prompt ingest` 让 agent 整理，人工 review 生成的
wiki 更新，需要给其他 AI 工具使用时再导出 confirmed context。

如果是 clone 仓库后的本地开发环境，使用 `pip install -e ".[dev]"`。

## 当前版本

v0.3.7 增加了面向 Claude custom connector 的 OAuth 远程 MCP HTTP endpoint，并提供受访问策略控制的 current draft 写入和 patch 提案工具。它同时保留 v0.3 系列能力：确定性脚手架、manifest 扫描、source card 模板、prompt 渲染、lint、current 导出、mini-kb 草稿、可选 Hermes skills、Obsidian 友好的 Markdown tags、机器可读索引、doctor、多 Agent 访问策略、实体上下文，以及 Claude Desktop MCP practical context tools。

Linta 默认不调用任何 LLM API。它提供安全结构和 prompt，真正的语义整理由你配置的 agent 在你的环境里完成。

## 核心目录

```text
human/                 用户本人写作区，AI 默认不编辑。
ai_kb/raw/             不可变事实源。
ai_kb/wiki/            AI 编译后的知识层。
ai_kb/wiki/entities/   人、团队、产品线、别名和关系上下文。
ai_kb/wiki/indexes/    机器可读 JSON 索引。
ai_kb/schema/          agent 维护规则。
ai_kb/export_for_ai/   给 ChatGPT / Claude / Gemini 等工具读取的消费层。
archive/               归档资料。
```

## 命令参考

v0.3.6 支持：

```bash
linta init ./MyKnowledgeBase
linta manifest scan ./MyKnowledgeBase
linta manifest scan ./MyKnowledgeBase --no-preserve-manual-fields
linta source-card create ./MyKnowledgeBase ai_kb/raw/meetings/example.md
linta prompt ingest ./MyKnowledgeBase ai_kb/raw/meetings/example.md
linta prompt entities ./MyKnowledgeBase ai_kb/raw/meetings/example.md
linta prompt tag ./MyKnowledgeBase ai_kb/wiki/projects/example.md
linta tags list ./MyKnowledgeBase/ai_kb/wiki/projects/example.md
linta tags add ./MyKnowledgeBase/ai_kb/wiki/projects/example.md --tag project/example
linta tags set ./MyKnowledgeBase/ai_kb/wiki/projects/example.md --tag status/draft
linta index build ./MyKnowledgeBase
linta raw import ./MyKnowledgeBase ~/Downloads/uploaded.md --source-type docs
linta maintenance daily ./MyKnowledgeBase
linta doctor ./MyKnowledgeBase
linta migrate ./MyKnowledgeBase --dry-run
linta agents wizard ./MyKnowledgeBase
linta agents status ./MyKnowledgeBase
linta claude-desktop config ./MyKnowledgeBase
linta claude-desktop status ./MyKnowledgeBase
linta claude-desktop project-instructions ./MyKnowledgeBase
linta mcp serve --agent claude-desktop --kb-root ./MyKnowledgeBase
linta mcp serve-http --kb-root ./MyKnowledgeBase --host 127.0.0.1 --port 8765
linta prompt lint-ai ./MyKnowledgeBase
linta lint ./MyKnowledgeBase
linta export current ./MyKnowledgeBase
linta mini-kb create ./MyKnowledgeBase --topic "Example" --purpose "Review prep"
linta hermes install-skills --dry-run
linta hermes status
linta hermes bootstrap-prompt ./MyKnowledgeBase
linta hermes configure-kb ./MyKnowledgeBase
python scripts/validate_example.py
```

## 安装后验证

初始化或配置 Hermes 后运行：

```bash
linta doctor ./MyKnowledgeBase
linta agents wizard ./MyKnowledgeBase
linta hermes status
```

`doctor` 检查知识库结构和确定性健康状态。`hermes status` 检查 skills、profiles 和默认知识库路径是否有效。

## 改名迁移

从旧名称升级到 Linta 后运行：

```bash
linta migrate ./MyKnowledgeBase --dry-run
linta migrate ./MyKnowledgeBase
```

迁移会在需要时把旧 `.llm-wiki/agent_access.yaml` 复制到 `.linta/agent_access.yaml`，把旧 `llm-wiki-tags` block 替换为 `linta-tags`，并报告旧 Hermes skills 目录。

## 多 Agent 访问策略

默认使用一个主读写 Agent，其他 Agent 只读：

```bash
linta agents wizard ./MyKnowledgeBase
linta agents status ./MyKnowledgeBase
```

策略写入知识库内部的 `.linta/agent_access.yaml`。常见配置是 Hermes 或 Codex 作为写入者，Claude Desktop 和 OpenClaw 只读。Claude Desktop 默认使用 `wiki_context`，可读取 confirmed/current wiki context、source cards、manifest、portfolio pages 和 indexes，但不读取 raw sources、current drafts、human notes 或 archive。

Claude Desktop 接入：

```bash
linta claude-desktop config ./MyKnowledgeBase
linta claude-desktop status ./MyKnowledgeBase
linta claude-desktop project-instructions ./MyKnowledgeBase
```

把生成的 MCP 片段加入 Claude Desktop 配置后重启应用。只读边界只适用于 Linta 提供的 MCP adapter；如果额外给 Claude Desktop 配置了 filesystem 或 shell 写权限，那些外部工具不受本项目强制约束。

Claude Desktop 推荐先调用 `context_overview`，再用 `context_search`、`context_read` 和
`context_bundle` 自行选择相关的已整理 wiki 上下文。这些 practical context tools 不读取
`ai_kb/raw/`；raw 仍然是主写入 Agent 使用的原始物料层。

把 `project-instructions` 的输出粘贴到 Claude Project instructions 中，Claude 就会按
Linta MCP 工具顺序读取整理后的上下文、引用 Linta path，并在上下文不足时说明缺口，而不是请求 raw。

`context_overview` 和 `context_bundle` 会返回 freshness signals，包括缺少 indexes、缺少
current、缺 source cards、manifest 不一致、current 可能过期和 lint errors。出现 warning 时，
Claude 应该先提示让主写入 Agent 执行 `linta maintenance daily`，再依赖这些上下文。

## Claude 远程 Connector

Claude App、Claude Desktop 的 web connector 和 Claude mobile 使用的是远程 MCP connector，
连接会从 Anthropic 云端发起。它们不能直接使用只存在于本机的 `stdio` MCP server；本地
`stdio` 机制只适用于 Claude Desktop 的本地配置。要让 Linta 在异地也可用，需要把 HTTP
MCP endpoint 部署到 Claude 能访问的公网 HTTPS 地址：

```bash
export LINTA_REMOTE_MCP_PUBLIC_BASE_URL="https://your-linta.example.com"
export LINTA_OAUTH_CLIENT_ID="replace-with-client-id"
export LINTA_OAUTH_CLIENT_SECRET="replace-with-client-secret"
export LINTA_OAUTH_APPROVAL_TOKEN="replace-with-private-approval-token"
linta mcp serve-http --kb-root ./MyKnowledgeBase --host 127.0.0.1 --port 8765
```

然后在这个本地进程前面放反向代理或 tunnel，并在 Claude custom connector 中填写公网 endpoint：

```text
https://your-linta.example.com/mcp
```

Claude connector 表单填写：

```text
Name: Linta
Remote MCP server URL: https://your-linta.example.com/mcp
OAuth Client ID: replace-with-client-id
OAuth Client Secret: replace-with-client-secret
```

Claude 打开 Linta 授权页时，输入 `LINTA_OAUTH_APPROVAL_TOKEN`。不要把真实域名、IP、token、
client secret 或个人知识库路径提交到 GitHub。真实值应放在 `.env`、部署平台 secret，或本机私有配置中。`.env.example` 只包含占位符。

远程写工具只有在 `.linta/agent_access.yaml` 里对应 agent 是 `mode: write` 时才会暴露。
内置写工具刻意保持较窄边界：

- `write_current_draft` 只能把 Markdown 写到 `ai_kb/wiki/current_draft/`。
- `propose_wiki_patch` 只会在 `ai_kb/wiki/current_draft/patches/` 下保存待 review patch。

它们不会编辑 `ai_kb/raw/`、`human/` 或 `archive/`，也不会把 draft 自动提升到
`ai_kb/wiki/current/`。

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

## 实体上下文

实体上下文位于 `ai_kb/wiki/entities/` 和 `ai_kb/wiki/portfolio/project_map.md`，用于维护稳定 ID、别名、人、团队、产品线、项目映射和带时间切片的关系。关系条目应尽量包含 `effective_from`、`effective_to`、`relationship_type`、`target_entity` 和 `source_path`，这样历史材料可以保留当时的组织语境。

使用 `linta prompt entities <kb_root> <raw_source>` 可以生成专门的实体更新 prompt。实体页不应写结论性人格评价，而应记录有来源支撑的行为模式、关注点、决策范围、沟通模式和历史 case。`linta index build` 除现有 source、project、capability、tag 索引外，还会生成 `entities.json`、`relationships.json` 和 `project_map.json`。

## 上传与每日维护

Hermes gateway 或聊天入口上传的文件，应先导入 raw：

```bash
linta raw import ./MyKnowledgeBase ~/Downloads/uploaded.md --source-type docs
```

每日维护不应该全量重新 ingest。运行：

```bash
linta maintenance daily ./MyKnowledgeBase
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
linta hermes bootstrap-prompt ./MyKnowledgeBase
linta hermes configure-kb ./MyKnowledgeBase
```

`bootstrap-prompt` 会输出给 Hermes Agent 执行的自然语言步骤；`configure-kb` 会写入 `~/.hermes/skills/linta/profiles/`。

## 后续路线

见 [ROADMAP.md](ROADMAP.md)。
