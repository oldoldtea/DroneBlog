# Design: Trellis AI Workflow Architecture Upgrade

## Task Tree

```
07-16-trellis-ai-workflow-upgrade (parent)
├── 07-16-spec-layer                # Child 1: establish spec layer
├── 07-16-ai-skills-refactor        # Child 2: refactor pipeline config
├── 07-16-unify-cli-mcp             # Child 3: unify entry points
└── 07-16-update-agents-workflow    # Child 4: update AGENTS.md
```

**Execution order**:

1. Child 1 and Child 2 can be done in parallel (they define specs and pipeline independently).
2. Child 3 depends on Child 2's pipeline semantics and uses Child 1's conventions.
3. Child 4 depends on Child 1-3 being complete (it documents the final state).
4. Parent performs final integration review after all children are archived.

## Architecture

### Before

```
User ──► bin/droneblog-pipeline.sh  ──► OpenAI API ──► nano editor ──► source/_posts/
      └──► bin/generate-and-archive.sh ──► GitHub dispatch
      └──► MCP Server (droneblog_mcp) ──► OpenAI/Kimi + Hexo (mature, but standalone)

AI specs:
  AGENTS.md  ──► .ai-skills/pipeline-executor.md
             ──► .ai-skills/pipeline-config.yml   (stale maple refs, non-existent commands)
             ──► .ai-skills/skills-registry.md    (skills.sh ecosystem, not local)

Trellis:
  .trellis/workflow.md + config.yaml + agents/ + scripts/  (skeleton, no spec/)
```

### After

```
User ──► MCP Client (Claude/Cursor) ──► droneblog_mcp (15 tools) ──► source/_posts/ + Hexo
      └──► bin/droneblog (lightweight CLI wrapper over MCP stdio) [optional]

AI specs (Trellis-native):
  .trellis/spec/guides/index.md
  .trellis/spec/droneblog_mcp/index.md
  .trellis/spec/droneblog_mcp/conventions.md
  .trellis/spec/droneblog_mcp/error-handling.md
  .trellis/spec/droneblog_mcp/testing.md
  .trellis/spec/droneblog_mcp/ai-workflow.md

Operational pipeline config:
  .ai-skills/pipeline-executor.md      (updated: Trellis phase-aware, MCP tool mapping)
  .ai-skills/pipeline-config.yml        (updated: kratos-rebirth, real MCP tools)
  .ai-skills/skills-registry.md         (updated: local skills only, no mandatory npx skills find)

Project guide:
  AGENTS.md                             (updated: Trellis + MCP + .ai-skills relationship)
```

## Key Contracts

### MCP Tool → Pipeline Stage Mapping

| Pipeline Stage (`.ai-skills`) | MCP Tool(s) | Notes |
|---|---|---|
| analysis | `pipeline_run` param `task_type` | `content_creation`, `config_change`, `theme_custom`, `debug_build`, `deploy` |
| skill_match | Prompts / Resources | `blog_writing`, `tech_analysis`, `blog_idea_generator` act as built-in skills |
| execute | `blog_generate`, `blog_list`, `blog_read`, `blog_edit`, `blog_delete`, `config_get`, `config_set`, `build`, `deploy` | Direct tool calls |
| compliance_audit | `pipeline_status` / `pipeline_run` internal | Log scan + stage gate verification |
| security | `scan_sensitive_info` utility (internal) | Already in `droneblog_mcp/utils/fs.py` |
| output | Tool result formatting | Standard report template in `pipeline-config.yml` |

### Spec Layer → Code Boundaries

- `.trellis/spec/guides/index.md` — cross-cutting rules (commit prefix, docs style, security).
- `.trellis/spec/droneblog_mcp/index.md` — package entry point + pre-dev checklist + quality check.
- `.trellis/spec/droneblog_mcp/conventions.md` — naming, typing, error messages.
- `.trellis/spec/droneblog_mcp/error-handling.md` — exception handling, user-facing messages, redaction.
- `.trellis/spec/droneblog_mcp/testing.md` — pytest conventions, test matrix, smoke tests.
- `.trellis/spec/droneblog_mcp/ai-workflow.md` — how AI assistants load specs, interact with MCP tools, write logs.

## Compatibility and Migration

- **No breaking change to Hexo build/deploy**: only AI-facing docs and scripts change.
- **MCP Server public interface unchanged**: 15 Tools / 5 Resources / 3 Prompts remain stable.
- **Shell scripts**: `droneblog-pipeline.sh` and `generate-and-archive.sh` will be deprecated/rewritten. If users have existing cron jobs or aliases, they should migrate to `bin/droneblog` wrapper or MCP client.
- **`.ai-pipeline.log`**: format preserved for backward compatibility; content updated to reflect MCP-driven stage signals.

## Rollback

- If a child task fails, it can be archived/rolled back independently without affecting others.
- Parent integration review can decide to delay Child 4 (AGENTS.md update) if earlier children introduce unresolved issues.
- All changes are confined to `.trellis/`, `.ai-skills/`, `bin/`, and `AGENTS.md`; reverting is a git reset of these paths.

## Operational Considerations

- `.ai-skills/` remains gitignored; spec additions under `.trellis/spec/` should be committed to share conventions.
- Child tasks will use `trellis-implement` / `trellis-check` sub-agents where appropriate.
- Final acceptance for parent: all children archived + `ruff` clean + pytest 42 passed + MCP interface matrix 51/51 still passes.
