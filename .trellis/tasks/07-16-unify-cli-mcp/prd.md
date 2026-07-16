# Child 3: 统一 CLI/MCP 入口：精简 `bin/` 脚本

## Goal

消除 `bin/` 中重复、跨平台差、依赖本地编辑器的旧脚本，让 MCP Server 成为唯一的 AI 工作流执行引擎；同时保留一个轻量 CLI wrapper 供命令行环境使用。

## Background

当前 `bin/` 有三个脚本：

- `setup-mcp-env.sh`：创建 Python venv 并安装 `droneblog_mcp`，仍有用。
- `droneblog-pipeline.sh`：直接调用 OpenAI API、nano 编辑器、写入 `source/_posts/`；与 MCP Server 功能重复，且 Windows 不友好。
- `generate-and-archive.sh`：直接调用 OpenAI API、nano 编辑器，然后通过 GitHub repository dispatch 归档；与 MCP setup/sync 模式重叠。

MCP Server 已经提供 15 个 tools，覆盖生成、编辑、构建、部署、配置、流水线。

## Requirements

1. **保留并更新 `setup-mcp-env.sh`**
   - 安装 `droneblog_mcp` 后，打印 Trellis 工作流提示（创建任务、加载 spec）。
   - 确保脚本在 bash/zsh 下可运行（Windows 用户改用 MCP 客户端或 Python）。

2. **重写 `droneblog-pipeline.sh` 为 `bin/droneblog` 轻量 wrapper**
   - 通过 stdio 启动 `droneblog-mcp serve`；
   - 发送 JSON-RPC `tools/call` 请求（`blog_generate`/`build` 等）；
   - 支持子命令：`generate`, `build`, `deploy`, `list`, `read`, `status`；
   - 从环境变量读取 `DRONEBLOG_DIR` 和 `OPENAI_API_KEY`；
   - 不重复实现 AI 生成或 Hexo 调用逻辑。

3. **移除 `generate-and-archive.sh`**
   - 其 GitHub dispatch 归档逻辑由 MCP `setup_sync_posts` 或 GitHub Actions 替代；
   - 在 AGENTS.md / README 中说明替代方式。

4. **确保 wrapper 不破坏现有测试**
   - wrapper 不修改 `droneblog_mcp` 源码；
   - 原有 pytest 42 项与 51 接口矩阵不受影响。

## Acceptance Criteria

- [ ] `bin/` 中无直接调用 OpenAI API 的 bash 脚本。
- [ ] `bin/droneblog` wrapper 能成功调用 `blog_generate` 和 `build`（本地手动验证即可，无需新增 CI）。
- [ ] `generate-and-archive.sh` 被删除或明确标记为 deprecated。
- [ ] `setup-mcp-env.sh` 文档更新，提及 Trellis + MCP workflow。
- [ ] 脚本变更不引入新的 uncommitted 测试产物。

## Out of Scope

- 不为 Windows 提供 PowerShell wrapper（MCP 客户端是 Windows 主入口）。
- 不新增 MCP tool（复用现有 15 个）。

## Notes

- CLI wrapper 的实现语言：推荐 Python（`subprocess` + JSON-RPC），便于跨平台；也可用 bash + `jq`，但依赖更多。
- 若用户仅通过 MCP 客户端使用，wrapper 的维护优先级较低，但保留可降低迁移阻力。
