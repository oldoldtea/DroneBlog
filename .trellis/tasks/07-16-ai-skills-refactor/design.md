# Design: `.ai-skills/` 流水线重构

## Current State

- `pipeline-config.yml`：声明式配置，但引用 `themes/hexo-theme-maple/_config.yml`，阶段定义与 AGENTS.md 不一致，`npx skills find` 为强制步骤。
- `pipeline-executor.md`：系统级执行规范，优先级仅次于用户指令，但动作矩阵面向 shell/nano，未映射 MCP tools。
- `skills-registry.md`：本地 skill 表包含大量未安装的第三方 skill 示例，且要求强制 find-skills 回退。

## Target State

- `pipeline-config.yml`：阶段、任务类型、检查项与 MCP tools 对齐；移除 maple 引用；`npx skills find` 改为可选提示。
- `pipeline-executor.md`：保留 Stage Gate 日志协议，但执行动作改为调用 MCP tools / reading pipeline_status；移除 nano 编辑器强制步骤。
- `skills-registry.md`：本地 skill 表仅保留实际存在或项目自定义 skill；find-skills 回退可选。

## MCP Tool Mapping

| Pipeline Stage | MCP Tool / Resource / Prompt | Notes |
|---|---|---|
| analysis | `pipeline_run(task_type=...)` | `content_creation`, `config_change`, `theme_custom`, `debug_build`, `deploy` |
| skill_match | Prompts `blog_writing`, `tech_analysis`, `blog_idea_generator` | Built-in skills |
| execute | `blog_generate`, `blog_list`, `blog_read`, `blog_edit`, `blog_delete`, `config_get`, `config_set`, `build`, `deploy` | Direct tool calls |
| compliance_audit | `pipeline_status` | Reads `.ai-pipeline.log` signals |
| security | Internal `scan_sensitive_info` | Already in `droneblog_mcp/utils/fs.py` |
| output | Tool result formatting | Standard report template |

## Conflict Resolution

- `pipeline-executor.md` 自声明优先级仅次于用户指令，高于 `AGENTS.md`。
- 本次重构后的 `pipeline-executor.md` 必须与 Trellis `workflow.md` 一致：阶段顺序、日志格式、合规审核不可跳过。
- 与 `AGENTS.md` 冲突时，以 `pipeline-executor.md` 为准（按其自身规则），但应在 `AGENTS.md` 中说明此优先级。

## Backward Compatibility

- `.ai-pipeline.log` 格式保持不变（timestamp/status/stage/message）。
- 旧 shell 脚本不再被规范引用，但 `.ai-pipeline.log` 仍可作为轻量审计日志。
