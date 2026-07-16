# Design: 更新 `AGENTS.md` 反映 Trellis + MCP 工作流

## Scope

仅修改 `AGENTS.md` 的「AI 工作流入口」章节（约第 281-319 行），不触碰项目概览、技术栈、目录结构、主题配置等已准确章节。

## 新四层结构

```
用户请求
  └──► AGENTS.md（项目级权威）
        └──► .trellis/workflow.md（Trellis 标准工作流）
              └──► .trellis/spec/（包级规范，可注入子任务）
                    └──► .ai-skills/pipeline-executor.md + pipeline-config.yml（流水线执行规范）
                          └──► droneblog_mcp（MCP Server，主执行入口）
                                └──► bin/droneblog（CLI wrapper，辅助入口）
```

## 关键更新点

1. **加载顺序**：明确 AI 助手读取顺序。
2. **入口说明**：MCP Server 为主，`bin/droneblog` 为辅。
3. **删除不存在引用**：`.githooks/`、`@command:extension.showGitCommit`。
4. **提交规范**：保留中文前缀，说明与 Trellis 任务分类并存。
5. **任务系统**：说明未来写博客/改配置/调主题应先创建 Trellis task，并引用博客任务模板。

## 冲突处理

- `AGENTS.md` 保护声明：本次修改已在前序对话中获得用户明确同意。
- 若 `.ai-skills/pipeline-executor.md` 与 `AGENTS.md` 冲突，以 `pipeline-executor.md` 为准（按其自身规则），但 `AGENTS.md` 应提示此优先级。

## Backward Compatibility

- 仅修改文档，不影响代码或构建。
