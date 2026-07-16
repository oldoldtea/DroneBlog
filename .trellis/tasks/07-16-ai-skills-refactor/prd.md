# Child 2: 重构 `.ai-skills/` 流水线配置

## Goal

将现有 `.ai-skills/` 流水线规范从"手写 shell 驱动"升级为"Trellis 阶段 + MCP tools"驱动的配置，清理过时引用，消除不可执行项。

## Background

当前 `.ai-skills/pipeline-config.yml` 仍引用 `themes/hexo-theme-maple/_config.yml`，且包含不可执行命令 `npx skills find` 和不存在工具 `@command:extension.showGitCommit`。`pipeline-executor.md` 的动作矩阵也未与 `droneblog_mcp` 的 15 Tools 对齐。

## Requirements

1. **修正事实性错误**
   - 所有 `hexo-theme-maple` 替换为 `kratos-rebirth`；
   - 主题配置路径更新为 `node_modules/hexo-theme-kratos-rebirth/_config.yml` 或 `_config.kratos-rebirth.yml`；
   - 删除或标记为可选的不可执行项（`npx skills find` 强制步骤改为可选提示）。

2. **阶段与 MCP tools 对齐**
   - `analysis`：由 `pipeline_run(task_type=...)` 触发；
   - `skill_match`：由 MCP Prompts（`blog_writing`/`tech_analysis`/`blog_idea_generator`）充当内置 skill；
   - `execute`：映射到 `blog_generate`/`blog_list`/`blog_read`/`blog_edit`/`blog_delete`/`config_get`/`config_set`/`build`/`deploy`；
   - `compliance_audit`：由 `pipeline_status` / `pipeline_run` 内部阶段门验证；
   - `security`：复用 `droneblog_mcp/utils/fs.py` 的 `scan_sensitive_info`；
   - `output`：工具返回标准报告格式。

3. **更新执行规范**
   - `pipeline-executor.md` 中 Stage Gate 日志格式保留，但验证方式改为可调用 `droneblog-mcp pipeline_status` 读取日志；
   - 移除"打开 nano 编辑器"的强制人工审核步骤（MCP 场景下无 TTY）；
   - 明确 `auto_confirm=true` 为默认，审阅在客户端对话中完成。

4. **更新 skills-registry.md**
   - 本地 skill 表仅保留实际存在的 skill（如 `find-skills`、`skill-creator` 可选）；
   - 删除硬编码的 Vercel/Anthropic 技能示例，或明确标注为"未安装示例"；
   - `npx skills find` 不再作为强制回退。

## Acceptance Criteria

- [ ] `.ai-skills/` 中无 `maple` 字符串残留。
- [ ] `pipeline-config.yml` 的 stage 与 MCP tool 映射表存在且准确。
- [ ] `pipeline-executor.md` 不再引用 `@command:extension.showGitCommit` 或 `nano`。
- [ ] `skills-registry.md` 将 `npx skills find` 标记为可选而非强制。
- [ ] 文件通过 YAML / Markdown 基本语法检查（无解析错误）。

## Out of Scope

- 不修改 `droneblog_mcp` 源码（在 Child 3 中通过 wrapper 使用）。
- 不删除 `.ai-pipeline.log` 格式（保持向后兼容）。

## Notes

- 修改 `.ai-skills/pipeline-executor.md` 时注意其声明"优先级仅次于用户指令"；新规范必须与 Trellis workflow.md 一致。
- 本任务完成后，Child 3 的 CLI wrapper 和 Child 4 的 AGENTS.md 应引用更新后的配置。
