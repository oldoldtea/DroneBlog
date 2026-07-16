# Implement Plan: 统一 CLI/MCP 入口

## Implementation Checklist

1. **新增 `bin/droneblog` Python wrapper**
   - [ ] 使用 `subprocess.Popen` 启动 `droneblog-mcp serve --transport stdio`。
   - [ ] 发送 `initialize` + `initialized` JSON-RPC。
   - [ ] 实现子命令：`generate`, `build`, `deploy`, `list`, `read`, `status`。
   - [ ] 从环境变量读取配置：`DRONEBLOG_DIR`, `OPENAI_API_KEY`/`DRONEBLOG_OPENAI_API_KEY`, `DRONEBLOG_MODEL`, `DRONEBLOG_TEMPERATURE`。
   - [ ] 打印用户友好的结果/错误。

2. **更新 `bin/setup-mcp-env.sh`**
   - [ ] 安装后提示 Trellis workflow 和 `bin/droneblog` 用法。
   - [ ] 检查 Python 版本 ≥ 3.11。

3. **删除旧脚本**
   - [ ] `git rm bin/droneblog-pipeline.sh`
   - [ ] `git rm bin/generate-and-archive.sh`

4. **验证**
   - [ ] `bin/droneblog status` 能返回 pipeline 状态（若环境配置正确）。
   - [ ] `bin/droneblog list` 能列出文章。
   - [ ] 旧脚本已不在 `bin/`。

## Validation Commands

```bash
ls bin/
python bin/droneblog --help
DRONEBLOG_DIR=. droneblog-mcp status  # baseline check
```

## Rollback

- 恢复旧脚本需从 git 历史检出。
- Wrapper 删除不影响 MCP Server。

## Notes

- 不在 Windows 提供 PowerShell wrapper；Windows 主入口为 MCP 客户端。
- 若 `droneblog-mcp` 不在 PATH，wrapper 应尝试 `.venv/bin/droneblog-mcp`。
