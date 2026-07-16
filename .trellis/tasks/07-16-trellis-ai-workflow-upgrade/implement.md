# Implement Plan: Trellis AI Workflow Architecture Upgrade

## Child Task Execution Order

```
Phase A (parallel):
  Child 1: 07-16-spec-layer
  Child 2: 07-16-ai-skills-refactor

Phase B (after A):
  Child 3: 07-16-unify-cli-mcp

Phase C (after B):
  Child 4: 07-16-update-agents-workflow

Phase D (parent):
  Integration review → spec update → batched commit
```

## Per-Child Deliverables

### Child 1 — 建立 `.trellis/spec` 规范层

- Create `.trellis/spec/guides/index.md`
- Create `.trellis/spec/droneblog_mcp/index.md` + conventions / error-handling / testing / ai-workflow
- Verify `python ./.trellis/scripts/get_context.py --mode packages` discovers the new spec layer
- Acceptance: at least 5 spec files exist, indexed, and contain actionable guidelines

### Child 2 — 重构 `.ai-skills/` 流水线配置

- Update `.ai-skills/pipeline-config.yml`: fix maple refs, align task types with MCP tools, make `npx skills find` optional, update output templates
- Update `.ai-skills/pipeline-executor.md`: reflect MCP tool mapping, remove non-existent commands, keep stage-gate logging intact
- Update `.ai-skills/skills-registry.md`: local-only skills, no mandatory external search
- Acceptance: `grep -i maple` returns nothing; stage names map to MCP tools; `npx skills find` is not a hard gate

### Child 3 — 统一 CLI/MCP 入口

- Decide fate of each `bin/` script:
  - `setup-mcp-env.sh`: keep, update to mention Trellis workflow
  - `droneblog-pipeline.sh`: rewrite as thin wrapper over `droneblog-mcp` stdio OR remove and document MCP client usage
  - `generate-and-archive.sh`: remove; archive-via-dispatch logic moves to MCP/CLI path or is deprecated
- Add `bin/droneblog` (optional) lightweight CLI that wraps MCP stdio for headless environments
- Acceptance: no duplicate AI generation logic between bash and Python; shell scripts are POSIX-compliant or removed

### Child 4 — 更新 `AGENTS.md`

- Rewrite "AI 工作流入口" chapter
- Add `.trellis/` → `.ai-skills/` → `droneblog_mcp` loading order
- Remove `.githooks/`, `@command:extension.showGitCommit`, and other non-existent references
- Acceptance: AGENTS.md matches the actual files on disk and the new workflow

## Validation Commands

Run after each child and at parent integration:

```bash
# Python / MCP quality
cd droneblog_mcp
ruff check .
pytest

# Hexo sanity (if config/content changed)
cd ..
hexo clean && hexo generate

# Trellis task state
python ./.trellis/scripts/task.py validate 07-16-<child>
```

## Risky Files / Rollback Points

- `AGENTS.md`: protected by "非必要不修改"; Child 4 must get explicit user consent per AGENTS.md rules before editing.
- `bin/droneblog-pipeline.sh`: if removed, any external cron/alias breaks; Child 3 must document migration path.
- `.ai-skills/pipeline-executor.md`: high-priority rules; changes must not conflict with `AGENTS.md` hierarchy.

## Commit Strategy

- One commit per child task (after its check passes).
- Parent integration commit only if no child left dirty state uncommitted.
- Do not push; the user controls remote sync.

## Before `task.py start` of First Child

- [x] Parent `prd.md` exists and reviewed
- [x] Parent `design.md` exists
- [x] Parent `implement.md` exists
- [ ] Child PRDs written (next step)
- [ ] User approves parent planning artifacts
