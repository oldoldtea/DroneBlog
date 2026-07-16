# droneblog_mcp — 包规范入口

> 本规范适用于所有修改 `droneblog_mcp/` 包（MCP Server）的 AI 助手。
> 修改前请先阅读本页 Pre-Development Checklist；修改后请对照 Quality Check 自查。

---

## 包定位

`droneblog_mcp` 是 DroneBlog 的 AI 主入口，提供：

- **15 个 MCP Tools**：博客生成、编辑、构建、部署、配置管理等。
- **5 个 MCP Resources**：博客列表、配置、文章、状态、模板。
- **3 个 MCP Prompts**：博客写作、技术分析、选题生成。

支持 stdio 与 SSE 两种传输方式，是 Claude Desktop / Cursor 等 MCP 客户端以及 `bin/droneblog` CLI wrapper 的调用目标。

---

## Pre-Development Checklist

在修改 `droneblog_mcp/` 任何代码前，确认已阅读以下规范：

- [ ] [conventions.md](./conventions.md) — Python 命名、类型提示、MCP 工具参数设计、返回格式。
- [ ] [error-handling.md](./error-handling.md) — 异常分类、用户错误消息、密钥脱敏、日志约束。
- [ ] [testing.md](./testing.md) — pytest 结构、测试夹具、接口矩阵、SSE 烟测。
- [ ] [ai-workflow.md](./ai-workflow.md) — AI 助手如何读取本包规范、调用 MCP tools、写 `.ai-pipeline.log`。
- [ ] [guides/index.md](../guides/index.md) — 跨包通用规范（提交、文档风格、安全基线、AI 加载顺序）。

---

## 关键约束

1. **MCP 接口稳定性**：现有 15 Tools / 5 Resources / 3 Prompts 的签名和语义不得破坏；新增工具/资源必须补充对应测试。
2. **密钥安全**：所有密钥读取自环境变量，工具结果中必须脱敏。
3. **Hexo 不可侵入**：MCP Server 只通过命令行调用 `hexo` 或读写 `source/_posts/`、`_config.yml` 等外部文件，不修改 Hexo 主题或生成器内部。
4. **日志结构化**：所有流水线操作写入 `.ai-pipeline.log`，遵循 `[timestamp] [status] [stage] message` 格式。

---

## Quality Check

修改完成后，按以下清单自查：

- [ ] 是否运行了 `cd droneblog_mcp && ruff check .` 且通过？
- [ ] 是否运行了 `cd droneblog_mcp && pytest` 且 42 个用例全部通过？
- [ ] 是否运行了接口矩阵验证（15 tools × 5 resources × 3 prompts 或等价覆盖）？
- [ ] 新增/修改的工具是否补充了对应的 pytest 用例？
- [ ] 是否扫描了新增文件中的敏感信息（`api_key`、`token`、`password`、`secret`、`private_key`）？
- [ ] 错误消息是否使用中文、用户可理解，且不含脱敏前的密钥？
- [ ] 是否在 `.ai-pipeline.log` 中记录了关键阶段信号（`[OK] [stage]` / `[FAIL] [stage]`）？
- [ ] 是否更新了相关 `.trellis/spec/` 文档（如果本次修改引入了新约定或新陷阱）？

---

## 快速链接

- `droneblog_mcp/` 源码：`droneblog_mcp/`
- 测试目录：`droneblog_mcp/tests/`
- 包配置：`pyproject.toml`（如存在）
- 流水线配置：`.ai-skills/pipeline-config.yml`
- 通用规范：`.trellis/spec/guides/index.md`
