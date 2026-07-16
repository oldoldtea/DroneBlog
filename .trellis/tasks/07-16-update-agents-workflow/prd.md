# Child 4: 更新 `AGENTS.md` 反映 Trellis + MCP 工作流

## Goal

重写 `AGENTS.md` 中"AI 工作流入口"章节，使其准确描述 Trellis 任务系统、`.trellis/spec/` 规范层、`.ai-skills/` 流水线配置与 `droneblog_mcp` MCP Server 之间的关系，并删除不存在的内容。

## Background

`AGENTS.md` 是面向 AI 助手的权威规范文件，受"非必要不修改"保护。此前的文档勘误已修正主题等技术事实，但"AI 工作流入口"仍指向旧的 `.ai-skills/` 驱动模式，且包含 `.githooks/`、`@command:extension.showGitCommit` 等不存在的引用。

## Requirements

1. **更新"AI 工作流入口"章节**
   - 明确加载顺序：`AGENTS.md` → `.trellis/workflow.md` → `.trellis/spec/` → `.ai-skills/pipeline-executor.md` → `.ai-skills/pipeline-config.yml`；
   - 说明 Trellis 任务系统用于"有明确交付项的工作"，`.ai-skills/` 用于"流水线执行规范"；
   - 说明 MCP Server 是主要执行入口，CLI wrapper（`bin/droneblog`）为辅助入口。

2. **删除不存在引用**
   - 移除 `.githooks/*`（目录不存在）；
   - 移除 `@command:extension.showGitCommit` 工具引用；
   - 移除"所有 Git 提交操作必须使用某工具"的强制要求，改为"AI 不代替用户执行 `git commit`/`git push`/`hexo deploy`，除非用户明确要求"。

3. **统一提交规范表述**
   - 保留简体中文前缀示例，但明确前缀与 Trellis 子任务分类可并存；
   - 增加说明：Trellis 任务产物（`.trellis/tasks/`）自身不参与博客构建，已 gitignored。

4. **与 Child 1-3 产出一致**
   - 引用 `.trellis/spec/droneblog_mcp/ai-workflow.md`；
   - 引用更新后的 `.ai-skills/pipeline-config.yml` 阶段定义；
   - 引用 `bin/droneblog` wrapper 的存在与用途。

## Acceptance Criteria

- [ ] `AGENTS.md` 中无 `.githooks` 或 `@command:extension.showGitCommit` 字符串。
- [ ] "AI 工作流入口"章节准确反映 Trellis + spec + `.ai-skills/` + MCP 四层结构。
- [ ] 提交规范与 Trellis 流程不冲突。
- [ ] 修改前向用户说明原因、具体位置、预期影响（已在本任务创建时获得同意）。

## Out of Scope

- 不修改 `AGENTS.md` 中项目概览、技术栈、目录结构、主题配置等已准确章节。
- 不引入新的 AI 工作流阶段。

## Notes

- 本任务必须在 Child 1-3 完成后执行，否则引用的文件/路径尚未确定。
- 受"非必要不修改"约束，每次编辑需最小化变更范围。
