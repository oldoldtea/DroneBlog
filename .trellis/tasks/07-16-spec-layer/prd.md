# Child 1: 建立 `.trellis/spec` 规范层

## Goal

补全当前 `.trellis/` 目录中缺失的 `spec/` 规范层，为后续 AI 驱动的代码修改提供可注入、可沉淀的项目级指南。

## Background

`.trellis/workflow.md` 已定义任务系统、spec 系统和工作流，但 `.trellis/spec/` 目录不存在。AI 助手在 Phase 2 执行时没有项目级规范可参考，只能依赖 `AGENTS.md` 和会话记忆。

## Requirements

1. 创建 `.trellis/spec/guides/index.md`：跨包通用指南（提交规范、文档风格、安全基线、AI 工作流加载顺序）。
2. 创建 `.trellis/spec/droneblog_mcp/index.md`：包入口，含 Pre-Development Checklist 和 Quality Check。
3. 创建 `.trellis/spec/droneblog_mcp/conventions.md`：Python 命名、类型提示、工具参数设计、返回格式。
4. 创建 `.trellis/spec/droneblog_mcp/error-handling.md`：异常分类、用户错误消息、密钥脱敏、日志约束。
5. 创建 `.trellis/spec/droneblog_mcp/testing.md`：pytest 结构、测试夹具、接口矩阵、SSE 烟测。
6. 创建 `.trellis/spec/droneblog_mcp/ai-workflow.md`：AI 助手如何读取本包规范、调用 MCP tools、写 `.ai-pipeline.log`。
7. 创建 `.trellis/task_templates/blog_post/`：含 `prd.md` 和 `implement.md`，用于快速创建"写一篇博客"任务。

## Acceptance Criteria

- [ ] `python ./.trellis/scripts/get_context.py --mode packages` 能发现 `guides` 和 `droneblog_mcp` 两个 spec 层。
- [ ] 每个 `index.md` 的 Pre-Development Checklist 至少指向 3 个具体指南文件。
- [ ] `.trellis/task_templates/blog_post/` 存在，且 `task.py create` 可通过 `--template blog_post` 使用（若 Trellis 脚本支持模板参数）或至少能被手动复制使用。
- [ ] 规范内容不与现有 `AGENTS.md` 冲突；冲突时明确优先级。
- [ ] 所有 `.md` 文件使用 UTF-8、LF 结尾。

## Out of Scope

- 不为 Hexo 博客本体建立 spec（不属于 AI 工程化范围）。
- 不引入外部 linter/format 配置（沿用已有 ruff）。

## Notes

- 规范写入后，Trellis 子任务执行时将通过 `implement.jsonl` / `check.jsonl` 注入这些文件。
- 本任务完成后，Child 2 / 3 / 4 应引用此处定义的规范。
