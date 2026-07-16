# Guides — 跨包通用规范

> 本目录存放跨包（package-agnostic）的通用指南，所有在 DroneBlog 项目上进行修改的 AI 助手都应优先阅读。
>
> 规范优先级（从高到低）：
> 1. 当前任务 `prd.md` / `design.md` / `implement.md` 中的明确要求
> 2. `AGENTS.md`（项目级权威说明）
> 3. `.trellis/spec/` 下相关包规范与本 `guides/index.md`
> 4. `.trellis/workflow.md`（Trellis 流程）
> 5. `.ai-skills/pipeline-executor.md` 与 `pipeline-config.yml`（AI 流水线执行规范）
> 6. 项目既有代码惯例

---

## Pre-Development Checklist

在 DroneBlog 项目上进行修改前，确认已阅读以下通用指南：

- [ ] [Git 提交规范](#1-git-提交规范) — 提交信息格式与多文件提交原则。
- [ ] [文档风格](#2-文档风格) — 文件编码、换行、Markdown/YAML 规范。
- [ ] [安全基线](#3-安全基线) — 敏感信息禁止提交、脱敏要求、安全审查必做项。
- [ ] [AI 工作流加载顺序](#4-ai-工作流加载顺序) — 新会话中的上下文加载顺序与入口。
- [ ] [Code Reuse Thinking Guide](./code-reuse-thinking-guide.md) — 避免重复代码、抽象时机。
- [ ] [Cross-Layer Thinking Guide](./cross-layer-thinking-guide.md) — 跨层数据流与边界检查。

---

## 1. Git 提交规范

### 1.1 语言与格式

- 提交信息使用**简体中文**，格式：`[分类] 简述修改内容`。
- 分类与对应路径（参考 `.ai-skills/pipeline-config.yml`）：

| 分类 | 前缀 | 典型修改路径 |
|------|------|--------------|
| 文章 | `[文章]` | `source/_posts/` |
| 配置 | `[配置]` | `_config.yml`、`_config.kratos-rebirth.yml` |
| 主题 | `[主题]` | `node_modules/hexo-theme-kratos-rebirth/`（注意：持久化主题定制应使用 `_config.kratos-rebirth.yml`） |
| 文档 | `[文档]` | `README.md`、`AGENTS.md`、`.trellis/spec/` |
| 依赖 | `[依赖]` | `package.json`、`package-lock.json`、`yarn.lock` |
| 修复 | `[修复]` | 通用 bug 修复 |
| 重构 | `[重构]` | 架构调整、工作流升级 |

### 1.2 示例

```text
[文章] 新增 Kafka 消息传输机制源码解析
[配置] 调整首页分页为每页 20 篇
[文档] 更新 AI 工作流入口说明
[依赖] 升级 hexo-theme-kratos-rebirth 至 v3.0.1
[修复] hexo_build 不再把"打印帮助"误判为构建成功
```

### 1.3 多文件提交原则

- 一个提交只包含一个逻辑变更；不要把文章、配置、依赖混在一起。
- 不要提交 `public/`、`.deploy_git/`、`node_modules/` 等被 `.gitignore` 忽略的内容。

---

## 2. 文档风格

### 2.1 文件格式

- 编码：**UTF-8**（无 BOM）。
- 换行：**LF**（`\n`），非 CRLF。
- 缩进：2 个空格（Markdown 列表、YAML 等）。
- 行尾：去除行尾空格，文件末尾保留一个空行。

### 2.2 Markdown 规范

- 使用 ATX 标题（`#`），标题层级连续，不跳过。
- 列表符号：无序列表用 `-`，有序列表用数字。
- 代码块标注语言（如 `bash`、`yaml`、`python`）。
- 表格对齐使用 `|` 和 `-` 标准 Markdown 表格语法。

### 2.3 YAML 规范

- 缩进 2 个空格，不使用 Tab。
- 字符串值根据是否需要转义选择是否加引号；URL、包含特殊字符的值建议加引号。
- 数组使用块序列（`- item`）。

---

## 3. 安全基线

### 3.1 禁止提交敏感信息

以下信息**不得**写入任何提交到 Git 仓库的文件：

- API Key、Admin API Key、Token
- 密码、Secret、Private Key
- 个人访问令牌（PAT）
- 部署仓库的凭据

### 3.2 脱敏要求

- 日志、错误消息、用户提示中显示密钥时，必须脱敏（例如只显示前 4 位 + `...`）。
- 环境变量中读取的密钥不应在工具结果中回显。
- 测试代码中不要硬编码真实密钥，使用 `monkeypatch` 或 fixture 注入占位符。

### 3.3 安全审查必做项

每次修改完成后，检查：

- 新增文件是否包含 `api_key`、`token`、`password`、`secret`、`private_key` 等模式？
- `.gitignore` 是否包含 `.ai-pipeline.log`、`node_modules/`、`public/`、`.env`、`.deploy*/`？
- 外部链接是否可访问且可信？

---

## 4. AI 工作流加载顺序

在新会话中，AI 助手应按以下顺序加载上下文：

1. `AGENTS.md` — 项目概览、技术栈、常用命令、AI 工作流入口。
2. `.trellis/workflow.md` — Trellis 阶段、任务系统、spec 系统、提交规则。
3. `.trellis/spec/` — 跨包通用指南与相关包级规范。
4. `.ai-skills/pipeline-executor.md` — 流水线执行引擎规范。
5. `.ai-skills/pipeline-config.yml` — 阶段定义、检查项、失败策略、输出模板。
6. 当前任务目录下的 `prd.md` / `design.md` / `implement.md`（如果存在）。

### 4.1 常用入口

- **MCP 客户端**（Claude Desktop / Cursor 等）：通过 `droneblog_mcp` 的 tools / resources / prompts 执行。
- **CLI wrapper**：`bin/droneblog`（轻量 Python wrapper，通过 stdio 调用 MCP Server）。
- **Trellis 任务**：`python ./.trellis/scripts/task.py create "<title>" --slug <name>`。

### 4.2 规范引用原则

- 当 `AGENTS.md` 与 `.trellis/spec/` 冲突时，以**更新更近、更具体**的文件为准；如果无法判断，向用户确认。
- 本 `guides/index.md` 中的规则适用于所有包；具体包的额外约束在 `.trellis/spec/<package>/` 下定义。

---

## 5. 思考指南

本目录同时提供以下思考指南，在编码前/中/后按需阅读：

| 指南 | 用途 | 何时阅读 |
|------|------|----------|
| [Code Reuse Thinking Guide](./code-reuse-thinking-guide.md) | 识别重复模式，减少重复代码 | 发现相似代码、新增工具函数时 |
| [Cross-Layer Thinking Guide](./cross-layer-thinking-guide.md) | 理清跨层数据流 | 改动涉及 3 层以上或跨层边界时 |

---

## 6. 核心原则

- 30 分钟思考能节省 3 小时调试。
- 在修改任何值之前，先搜索其所有出现位置。
- 规范不是束缚，而是避免重复踩坑的共享记忆。
