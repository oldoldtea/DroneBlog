# 架构级升级：按 Trellis 规范重构 DroneBlog AI 工作流

## Goal

将 DroneBlog 的 AI 辅助工作流从当前"半自动化 shell 脚本 + 静态 Markdown 规范"模式，升级为符合 [Trellis](https://docs.trytrellis.app/zh) 规范的、可复现、可审计、可多人协作的 AI 工程化工作流。升级后，AI 助手应能：

1. 按 Trellis 阶段（Plan → Execute → Finish）和任务产物（PRD/Design/Implement）工作；
2. 读取项目级 spec 与技能规范，而不是依赖会话记忆；
3. 通过标准化入口（MCP Server / CLI）驱动内容生成、构建验证、部署等全流程；
4. 沉淀经验教训到 `.trellis/spec/`，实现持续进化。

## Background

项目当前已存在以下 AI 相关设施：

- **`.trellis/`**：Trellis 骨架已初始化（`workflow.md`、`config.yaml`、脚本、`agents/`），但**缺少 `spec/` 规范层**；没有运行过 Trellis 任务。
- **`.ai-skills/`**：手写 AI 流水线规范（`pipeline-executor.md`、`pipeline-config.yml`、`skills-registry.md`），驱动"混合式流水线"。该体系存在与现状脱节的问题：
  - `pipeline-config.yml` 仍引用 `themes/hexo-theme-maple/_config.yml`；
  - 阶段定义（analysis / skill_match / execute / compliance_audit / security / output）与 AGENTS.md 中的"5 阶段"图示不一致；
  - 存在不可执行项：`npx skills find` 依赖外部 skills.sh 生态、`@command:extension.showGitCommit` 工具并不存在；
  - 未与 MCP Server 打通。
- **`bin/`**：`droneblog-pipeline.sh`、`generate-and-archive.sh`、`setup-mcp-env.sh` 三个 bash 脚本，功能重叠、依赖 `OPENAI_API_KEY` 明文环境变量、`nano` 编辑器，跨平台差，无法被 MCP 客户端调用。
- **`droneblog_mcp/`**：已加固为 15 Tools / 5 Resources / 3 Prompts 的 MCP Server，支持 stdio/SSE、跨平台、密钥脱敏、端到端测试通过（51/51）。这是目前最成熟的 AI 入口，但**未与 `.ai-skills/` 流水线语义对齐**。
- **`AGENTS.md`**：项目规范文档，已按当前主题修正；其中"AI 工作流入口"章节仍指向旧 `.ai-skills/` 体系。

## Requirements

### R1 — Trellis 规范层补全

建立 `.trellis/spec/`：

- 至少包含 `guides/index.md`（跨包通用指南）与一个针对 `droneblog_mcp` 包（或根项目包）的 spec 层（`conventions.md`、`error-handling.md`、`testing.md`、`ai-workflow.md`）；
- 规范应覆盖：Python 代码风格、MCP 工具设计、错误消息规范、测试要求、AI 流水线阶段协议、Git 提交前缀。

### R2 — AI 工作流架构统一

将 `.ai-skills/` 体系重构为 Trellis 兼容的 AI 工作流规范：

- 清理已过时引用（maple 主题、不存在的命令/工具）；
- 明确 AI 工作的两种入口：
  1. **MCP 客户端**（Claude Desktop / Cursor 等）：通过 `droneblog_mcp` 的 tools/resources/prompts 执行；
  2. **CLI 脚本**（保留 `bin/droneblog-pipeline.sh` 的轻量场景）：调用 MCP Server 或直接调用 Python 包，避免重复实现；
- 让 MCP Server 的 `pipeline_run` / `blog_generate` / `build` / `deploy` 等工具与流水线阶段语义一致；
- 移除或重写 `generate-and-archive.sh`，其 GitHub dispatch 归档逻辑应收敛到 MCP/CLI 统一路径。

### R3 — 任务与上下文可持久化

- 启用 `.trellis/tasks/` 任务系统：未来每次"写博客/改配置/调主题"都以 Trellis task 形式创建、规划、执行、归档；
- 新增 `.trellis/task_templates/blog_post/` 模板，让博客写作任务可快速创建；
- `.ai-pipeline.log` 继续保留作为轻量运行日志，但增加结构化摘要；
- 关键研究/决策写入 `.trellis/tasks/<task>/research/`，而不是留在聊天上下文。

### R4 — AGENTS.md 与 Trellis 对齐

更新 `AGENTS.md` 的"AI 工作流入口"章节：

- 将 `.ai-skills/` 描述为"技能与流水线配置"，`.trellis/` 描述为"任务/规范/标准工作流"；
- 删除不存在的内容（如 `.githooks/`、`@command:extension.showGitCommit`）；
- 明确 AI 助手在新会话中的加载顺序：先 `AGENTS.md` → `.trellis/workflow.md` → `.ai-skills/pipeline-executor.md` → `pipeline-config.yml`。

### R5 — 不破坏现有功能

- MCP Server 的 15 Tools / 5 Resources / 3 Prompts 必须继续工作；
- Hexo 博客构建、部署路径不受影响；
- 已有 42 个 pytest 用例与端到端 51 接口矩阵保持通过。

## Acceptance Criteria

- [ ] `.trellis/spec/guides/index.md` 与至少一个包 spec 层存在且可被 `get_context.py --mode packages` 发现；
- [ ] `.trellis/task_templates/blog_post/` 存在，可用于快速创建博客写作任务；
- [ ] `.ai-skills/pipeline-config.yml` 中无 `hexo-theme-maple` 等过时引用，阶段/工具映射与 MCP Server 一致；
- [ ] `AGENTS.md` 的 AI 工作流入口章节反映 Trellis + MCP + `.ai-skills/` 的新关系，无不存在命令；
- [ ] `bin/` 脚本数量精简或职责明确：`setup-mcp-env.sh` 保留；`droneblog-pipeline.sh` 与 `generate-and-archive.sh` 至少有一个被重写/合并为调用 MCP Server 或 Python 包；
- [ ] 新增/重写的规范文件通过 ruff 与 pytest 不引入回归；
- [ ] 规划产物（本 `prd.md` + `design.md` + `implement.md`）完成并通过用户 review。

## Out of Scope

- 不迁移 Hexo 主题或重写博客主题模板；
- 不替换 GitHub Pages 部署机制；
- 不引入外部 skills.sh 生态依赖（`npx skills find` 保留为可选提示，不作为强制步骤）；
- 不修改已发布文章内容。

## Decisions (Made)

1. **AI 工作流主入口**：以 `droneblog_mcp` 的 MCP Server 为主入口；shell 脚本精简为轻量 wrapper，不再独立维护两套语义。
2. **任务拆分**：本任务作为**父任务**，拆分为 4 个可独立验证的**子任务**：
   - Child 1：建立 `.trellis/spec/` 规范层
   - Child 2：重构 `.ai-skills/` 流水线配置与执行规范
   - Child 3：统一 CLI/MCP 入口（精简/重写 `bin/` 脚本）
   - Child 4：更新 `AGENTS.md` 反映 Trellis + MCP 新工作流
3. **CLI wrapper**：保留 `bin/droneblog` 轻量 Python wrapper，通过 stdio 调用 MCP Server，供命令行环境使用。
4. **博客任务模板**：新增 `.trellis/task_templates/blog_post/` 模板（含 `prd.md`、`implement.md`），让"每次写博客都以 Trellis task 形式执行"可落地。

## Open Questions

- 无。所有关键架构与范围决策已确认。
