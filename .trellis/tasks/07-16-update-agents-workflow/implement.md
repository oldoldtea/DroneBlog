# Implement Plan: 更新 `AGENTS.md`

## Implementation Checklist

1. **读取当前 AGENTS.md 全文**
   - [ ] 确认「AI 工作流入口」章节起止位置。

2. **重写「AI 工作流入口」章节**
   - [ ] 更新加载顺序图。
   - [ ] 更新文件职责表（增加 `.trellis/` 各目录、更新 `.ai-skills/` 描述、增加 `bin/droneblog`）。
   - [ ] 删除 `.githooks/*` 行。
   - [ ] 删除 `@command:extension.showGitCommit` 引用。
   - [ ] 修改提交规则表述：AI 不代替用户执行 `git commit`/`git push`/`hexo deploy`。
   - [ ] 更新流水线总览，与 `pipeline-config.yml` 的 6 阶段一致。

3. **最小化变更**
   - [ ] 只修改「AI 工作流入口」章节，不改动其他章节。
   - [ ] 保留 AGENTS.md 保护声明。

4. **验证**
   - [ ] `grep ".githooks" AGENTS.md` 无结果。
   - [ ] `grep "@command:extension.showGitCommit" AGENTS.md` 无结果。
   - [ ] `grep "Trellis" AGENTS.md` 至少出现 3 次。
   - [ ] `grep "droneblog_mcp" AGENTS.md` 至少出现 2 次。

## Validation Commands

```bash
grep -n "AI 工作流入口" AGENTS.md
grep ".githooks" AGENTS.md || true
grep "@command:extension.showGitCommit" AGENTS.md || true
```

## Rollback

`git checkout AGENTS.md` 即可。

## Notes

- 本任务必须在 Child 1-3 完成后执行，因此应作为最后一个子任务 dispatch。
- 执行前需再次确认用户同意修改 AGENTS.md（可在 dispatch 时说明已在前序对话获得同意）。
