# Design: 统一 CLI/MCP 入口

## Current State

- `bin/setup-mcp-env.sh`：有用，但缺少 Trellis 工作流提示。
- `bin/droneblog-pipeline.sh`：直接调用 OpenAI API、nano、hexo；与 MCP Server 重复。
- `bin/generate-and-archive.sh`：直接调用 OpenAI API、nano、GitHub dispatch；与 MCP setup/sync 重叠。

## Target State

- `bin/setup-mcp-env.sh`：保留并增强，安装后提示 Trellis + MCP workflow。
- `bin/droneblog`：新增 Python wrapper，通过 stdio 调用 `droneblog-mcp serve`。
  - 子命令：`generate`, `build`, `deploy`, `list`, `read`, `status`。
  - 从环境变量读取 `DRONEBLOG_DIR`、`OPENAI_API_KEY`/`DRONEBLOG_OPENAI_API_KEY`、`DRONEBLOG_MODEL` 等。
  - 不重复实现 AI 生成或 Hexo 调用。
- `bin/droneblog-pipeline.sh` 与 `bin/generate-and-archive.sh`：删除。

## Wrapper Architecture

```
User ──► bin/droneblog generate "topic" "category" "tag1,tag2"
          └──► Popen("droneblog-mcp", "serve", "--transport", "stdio", env=...)
                └──► JSON-RPC initialize → tools/call blog_generate → result
          └──► 输出结果/错误到终端
```

## Tool Mapping

| CLI 子命令 | MCP Tool | 关键参数 |
|---|---|---|
| `generate <topic> [category] [tags]` | `blog_generate` | `topic`, `category`, `tags`, `slug` |
| `build [--no-clean]` | `build` | `clean` |
| `deploy` | `deploy` | `build_first=true` |
| `list` | `blog_list` | `limit=20` |
| `read <slug>` | `blog_read` | `slug` |
| `status` | `pipeline_status` | — |

## Error Handling

- MCP server 启动失败：提示检查 `DRONEBLOG_DIR` 和安装。
- Tool 返回 error：打印错误消息（已脱敏）。
- JSON-RPC 协议错误：打印 stderr 尾部供排查。

## Backward Compatibility

- 删除旧脚本前，在 README/AGENTS.md 中说明迁移路径。
- Wrapper 不修改 `droneblog_mcp` 源码，不影响现有测试。
