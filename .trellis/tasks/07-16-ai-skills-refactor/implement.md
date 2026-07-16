# Implement Plan: `.ai-skills/` 流水线重构

## Implementation Checklist

1. **修正 `pipeline-config.yml`**
   - [ ] 替换所有 `hexo-theme-maple` 为 `kratos-rebirth`
   - [ ] 更新主题配置路径为 `node_modules/hexo-theme-kratos-rebirth/_config.yml` 或 `_config.kratos-rebirth.yml`
   - [ ] 将阶段定义与 MCP tools 对齐，增加 `mcp_tool_mapping` 表
   - [ ] 将 `npx skills find` 从强制步骤改为可选提示
   - [ ] 更新输出模板，移除对不存在工具的引用
   - [ ] 更新 git_commit 路径映射（`themes/` → `node_modules/hexo-theme-kratos-rebirth/` 主题变更通常不提交）

2. **修正 `pipeline-executor.md`**
   - [ ] 保留 Stage Gate 日志格式
   - [ ] 将"打开 nano 编辑器"改为"MCP 客户端对话内审阅"
   - [ ] 将执行动作改为 MCP tool calls / `droneblog-mcp` CLI
   - [ ] 移除 `@command:extension.showGitCommit` 引用
   - [ ] 更新每轮回复自检清单（C1-C5），移除不可执行的 C4 强制要求

3. **修正 `skills-registry.md`**
   - [ ] 删除或明确标注未安装的第三方 skill 示例
   - [ ] 将 `npx skills find` 标记为可选
   - [ ] 保留 `find-skills` / `skill-creator` 作为可选 skill

4. **验证**
   - [ ] `grep -R "hexo-theme-maple" .ai-skills` 无结果
   - [ ] `grep -R "@command:extension.showGitCommit" .ai-skills` 无结果
   - [ ] YAML/Markdown 语法解析无误

## Validation Commands

```bash
grep -R "hexo-theme-maple" .ai-skills/ || true
grep -R "@command:extension.showGitCommit" .ai-skills/ || true
python -c "import yaml; yaml.safe_load(open('.ai-skills/pipeline-config.yml'))"
```

## Rollback

Git 还原 `.ai-skills/` 三个文件即可。
