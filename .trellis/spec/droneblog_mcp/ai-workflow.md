# droneblog_mcp — AI 助手工作流指南

> 本文件描述 AI 助手如何读取本包规范、调用 MCP tools、记录 `.ai-pipeline.log`。

---

## 1. 规范加载顺序

在操作 `droneblog_mcp` 或博客内容前，AI 助手应按以下顺序加载上下文：

1. `AGENTS.md` — 项目概览、技术栈、部署路径。
2. `.trellis/workflow.md` — Trellis 阶段、任务系统、spec 注入规则。
3. `.trellis/spec/guides/index.md` — 跨包通用规范（提交、文档风格、安全、AI 加载顺序）。
4. `.trellis/spec/droneblog_mcp/index.md` — 本包入口与 Pre-Development Checklist。
5. `.trellis/spec/droneblog_mcp/conventions.md` — Python / MCP 代码约定。
6. `.trellis/spec/droneblog_mcp/error-handling.md` — 异常分类、消息、脱敏、日志。
7. `.trellis/spec/droneblog_mcp/testing.md` — 测试要求。
8. 当前任务 `prd.md` / `design.md` / `implement.md`（如存在）。

---

## 2. MCP 工具映射表

AI 助手执行博客/配置/部署任务时，优先使用以下工具映射（与 `.ai-skills/pipeline-config.yml` 阶段对齐）：

| 阶段 | 可用工具 | 用途 |
|------|----------|------|
| analysis | `pipeline_run`（参数 `task_type`） | 明确任务类型：content_creation / config_change / theme_custom / debug_build / deploy |
| skill_match | `prompts/blog_idea_generator`、`prompts/blog_writing`、`prompts/tech_analysis` | 获取写作灵感、加载内置提示词 |
| execute | `blog_generate`、`blog_list`、`blog_read`、`blog_edit`、`blog_delete`、`config_get`、`config_set`、`build`、`deploy`、`setup_init`、`setup_status`、`setup_sync_posts`、`setup_update_config` | 实际执行内容或配置变更 |
| compliance_audit | `pipeline_status` 或内部日志扫描 | 检查阶段信号是否完整 |
| security | `scan_sensitive_info`（内部工具） | 扫描密钥、token、password 等 |
| output | 工具结果格式化 | 按 `.ai-skills/pipeline-config.yml` 输出模板汇报 |

### 2.1 内容创作任务（content_creation）

标准流程：

1. 确认标题、分类、标签（使用 `.ai-skills/pipeline-config.yml` 标准）。
2. 文件名：`{技术名缩写}-{内容主题}-{内容类型}.md`，小写、短横线、ASCII 字符。
3. 调用 `blog_generate` 生成文章到 `source/_posts/`。
4. 调用 `blog_read` 校验 Front-matter 和正文。
5. 调用 `build` 验证 `hexo clean && hexo generate` 通过。
6. 记录 `.ai-pipeline.log` 阶段信号。

### 2.2 配置调整任务（config_change）

1. 调用 `config_get` 读取当前配置。
2. 修改配置并调用 `config_set` 写回（只修改必要字段）。
3. 调用 `build` 验证构建无异常。
4. 记录日志。

### 2.3 部署任务（deploy）

- 仅在用户明确要求时执行 `deploy`。
- 部署前必须确认工作树无未保存变更（`confirm_no_unsaved_changes`）。
- 部署前执行 `build`。

---

## 3. 内容标准

### 3.1 Front-matter 要求

```yaml
---
title: 文章标题
date: 2026-07-16 10:00:00
tags:
  - 核心技术/语言
  - 主题方向
categories:
  - 6 选 1
---
```

- `title`：必填，建议格式 `{技术名} {内容类型}`。
- `date`：必填，格式 `YYYY-MM-DD HH:mm:ss`。
- `tags`：2-3 个，第 1 个为核心技术/语言，第 2 个为主题方向，第 3 个可选细分领域。
- `categories`：单一分类，6 选 1：后端开发 / 前端技术 / 系统编程 / 云原生 / 人工智能 / 分布式系统。

### 3.2 文件名规范

- 格式：`{技术名缩写}-{内容主题}-{内容类型}.md`
- 小写、短横线连接、ASCII 字符。
- 示例：`cpp-core-features.md`、`kafka-message-transmission.md`。
- 禁止：中文文件名、空格、下划线、驼峰、无意义缩写。

---

## 4. 日志记录

### 4.1 必须记录的信号

每次通过 MCP 工具执行博客任务时，在 `.ai-pipeline.log` 中追加：

```text
[{timestamp}] [START] [{stage}] {message}
[{timestamp}] [OK] [{stage}] {message}
[{timestamp}] [FAIL] [{stage}] {message}
[{timestamp}] [ROLLBACK] [{stage}] {message}
```

### 4.2 示例

```text
[2026-07-16 10:00:00] [START] [analysis] 用户请求：写一篇 Kafka 消息传输机制源码解析
[2026-07-16 10:00:05] [OK] [analysis] 任务类型：content_creation
[2026-07-16 10:00:06] [OK] [skill_match] 使用 blog_writing prompt
[2026-07-16 10:00:30] [OK] [execute] 生成文章 kafka-message-transmission.md
[2026-07-16 10:00:35] [OK] [execute] Hexo 构建成功
[2026-07-16 10:00:36] [OK] [security] 未发现敏感信息
[2026-07-16 10:00:37] [OK] [output] 任务完成，文章已生成并验证
```

### 4.3 日志安全

- 日志中不得出现完整密钥。
- 工具调用失败时，记录错误类别（`USER_ERROR` / `SYSTEM_ERROR` / `INTERNAL_ERROR`），不记录堆栈。

---

## 5. 与用户交互

### 5.1 执行前确认

- 部署、删除文章、修改 `_config.yml` 核心字段前，向用户确认。
- 生成文章时，可先提供标题/大纲让用户确认，再调用 `blog_generate`。

### 5.2 结果汇报

按 `.ai-skills/pipeline-config.yml` 的 `output_templates.default_report` 格式汇报：

- 修改摘要
- 文件清单（operation + path）
- 验证结果（✅ / ❌）
- 已加载 Skill / Prompt
- 后续建议

---

## 6. 禁止行为

- 不要直接修改 `node_modules/hexo-theme-kratos-rebirth/` 下的文件；持久化主题配置应使用 `_config.kratos-rebirth.yml`。
- 不要代替用户执行 `git commit`、`git push`、`hexo deploy`（除非用户明确同意）。
- 不要在工具结果中回显环境变量里的完整密钥。
- 不要跳过 `build` 验证直接生成/部署。
- 不要违反 `error-handling.md` 中的异常分类和消息规范。
