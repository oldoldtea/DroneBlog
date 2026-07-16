# Design: `.trellis/spec` 规范层与博客任务模板

## Spec 目录结构

```
.trellis/spec/
├── guides/
│   └── index.md                  # 跨包通用指南入口
└── droneblog_mcp/
    ├── index.md                  # 包 spec 入口 + Pre-Dev Checklist + Quality Check
    ├── conventions.md            # Python / MCP 命名与代码约定
    ├── error-handling.md         # 异常、错误消息、密钥处理
    ├── testing.md                # pytest、接口矩阵、SSE 烟测
    └── ai-workflow.md            # AI 助手如何与本包交互
```

## 规范内容来源

| 规范文件 | 主要来源 | 目标读者 |
|---|---|---|
| `guides/index.md` | Trellis workflow.md、AGENTS.md、项目既有约定 | 所有 AI 助手 |
| `droneblog_mcp/index.md` | 本包实际结构、pyproject.toml、tests/ | 修改 MCP 包的 AI 助手 |
| `conventions.md` | 现有代码（FastMCP 工具注册、Pydantic 模型） | implement agent |
| `error-handling.md` | 加固阶段发现的问题（F9/F10/F11） | implement/check agent |
| `testing.md` | 当前 42 pytest + 51 接口矩阵 | implement/check agent |
| `ai-workflow.md` | `.ai-skills/` 流水线 + MCP tools | AI 助手操作博客 |

## 任务模板设计

```
.trellis/task_templates/blog_post/
├── prd.md
└── implement.md
```

- `prd.md` 预填博客写作的 Goal、Requirements（Front-matter、文件名、分类/标签白名单）、Acceptance Criteria。
- `implement.md` 预填执行顺序：创建文章 → 校验 → 构建 → 输出规范。

## 与现有文件的关系

- 不删除 `AGENTS.md`；`AGENTS.md` 仍作为项目级权威，`.trellis/spec/` 作为包级/任务级可注入规范。
- `.ai-skills/pipeline-config.yml` 中的检查项（tags 2-3、categories 6 选 1）在 `ai-workflow.md` 中引用。

## 兼容性

- 新增文件全部在 `.trellis/` 下，不参与 Hexo 构建，不影响 MCP 运行时。
- 规范文件本身不参与 gitignored（除 `.trellis/tasks/` 和 `.trellis/workspace/` 外）。
