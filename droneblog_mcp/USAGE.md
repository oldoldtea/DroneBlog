# DroneBlog MCP Server 使用指南

## 打包

### Wheel 包

```bash
cd droneblog_mcp
source ../.venv/bin/activate          # Python 3.11+
python -m build --wheel --outdir dist
```

输出：`dist/droneblog_mcp-0.2.0-py3-none-any.whl`（以及 `.tar.gz`，若同时构建 sdist）。

> 构建产物（`dist/`、`*.whl`、`*.tar.gz`）**不纳入版本控制**，由 `.gitignore` 排除。请勿提交预构建 wheel。

### 本地开发模式

```bash
cd droneblog_mcp
pip install -e ".[dev]"
```

## 安装

### 方式一：一键配置（推荐）

```bash
bin/setup-mcp-env.sh        # 创建 .venv 并 pip install -e ".[dev]"，含导入自检
source .venv/bin/activate
droneblog-mcp version
```

### 方式二：手动安装

```bash
python3.11 -m venv .venv
source .venv/bin/activate
cd droneblog_mcp
pip install -e ".[dev]"
droneblog-mcp version
```

### 方式三：从 wheel 安装

```bash
pip install dist/droneblog_mcp-0.2.0-py3-none-any.whl
```

## 配置

### 环境变量

```bash
export DRONEBLOG_DIR=/path/to/your/blog                 # 博客工作目录（必需）
export OPENAI_API_KEY=sk-...                            # AI 生成（生成时必需）
export DRONEBLOG_OPENAI_BASE_URL=https://api.openai.com/v1  # 兼容/代理端点（可选）
export DRONEBLOG_MODEL=gpt-4o-mini                      # 默认模型（可选）
export DRONEBLOG_TEMPERATURE=0.7                        # 生成温度（可选）
export DRONEBLOG_MAX_TOKENS=4000                        # 最大 token 数（可选）
export DRONEBLOG_GITHUB_TOKEN=ghp_...                   # GitHub PAT（可选，推荐）
```

> 也可复制仓库根目录的 `.env.example` 为 `.env` 填写；`.env` 已被 `.gitignore` 排除。

### MCP 客户端配置（Claude Desktop）

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "droneblog": {
      "command": "droneblog-mcp",
      "args": ["serve", "--transport", "stdio"],
      "env": {
        "DRONEBLOG_DIR": "/path/to/your/blog",
        "OPENAI_API_KEY": "sk-..."
      }
    }
  }
}
```

> stdio 模式下服务默认**完全静默**（stdout 仅供 JSON-RPC）。排查时追加 `--verbose`，诊断信息输出到 stderr，不会污染协议通道。

## 命令行使用

```bash
droneblog-mcp version

# 初始化 GitHub 绑定（token 取自 DRONEBLOG_GITHUB_TOKEN 或交互式输入；--token 不推荐）
droneblog-mcp setup --mode local      # 本地模式（手动 hexo deploy）
droneblog-mcp setup --mode sync       # 同步归档模式（GitHub Actions 自动部署）

# 查看状态
DRONEBLOG_DIR=/path/to/blog droneblog-mcp status

# 启动 MCP Server
droneblog-mcp serve                                                # stdio（默认）
droneblog-mcp serve --transport sse --host 0.0.0.0 --port 8765     # SSE
droneblog-mcp serve --dir /path/to/blog --verbose                  # 指定目录 + stderr 横幅
```

## 可用 Tools（15）

| Tool | 功能 | 示例参数 |
|------|------|----------|
| `setup_init` | 初始化 GitHub 绑定 | `{"mode": "local"}`（token 取环境变量） |
| `setup_status` | 查看绑定状态 | `{}` |
| `setup_sync_posts` | 同步文章到 GitHub | `{}` |
| `setup_update_config` | 更新配置（返回值 token 已脱敏） | `{"sync_mode": "sync"}` |
| `blog_generate` | 生成博客文章 | `{"topic": "C++20 协程", "slug": "cpp20-coroutines", "category": "系统编程", "tags": ["C++", "协程"]}` |
| `blog_list` | 列出文章 | `{"category": "后端开发", "limit": 10}` |
| `blog_read` | 读取文章 | `{"slug": "tokio-async-runtime"}` |
| `blog_edit` | 编辑文章 | `{"slug": "xxx", "title": "新标题"}` |
| `blog_delete` | 删除文章 | `{"slug": "xxx", "confirm": true}` |
| `config_get` | 获取配置 | `{"scope": "site"}` |
| `config_set` | 修改配置 | `{"scope": "site", "key": "title", "value": "新标题"}` |
| `build` | 构建站点 | `{"clean": true}` |
| `deploy` | 部署站点 | `{"build_first": true}` |
| `pipeline_status` | 查看流水线状态 | `{}` |
| `pipeline_run` | 执行完整流水线 | `{"task_type": "debug_build", "params": {}}` |

### `blog_generate` 要点

- `slug`：**纯中文 `topic` 必须显式提供 `slug`**（kebab-case）。否则工具返回清晰错误，不会写出 `source/_posts/.md`。
- `auto_confirm`：默认 `true`。MCP 场景下**不会**打开本地编辑器（无 TTY 会卡死）；生成的正文通过返回值的 `draft` 字段回传，由客户端在对话中审阅/改写后再 `blog_edit` 定稿。
- `auto_deploy`：`true` 时按配置模式自动部署（local → `hexo deploy`；sync → 提交 GitHub 触发 Actions）。

## 可用 Resources

| Resource | 内容 |
|----------|------|
| `blog://{slug}` | 单篇文章 Markdown（模板） |
| `blogs://list` | 文章列表（collection；与 `blog://{slug}` 区分，避免路由冲突） |
| `config://site` | 站点配置 YAML |
| `config://theme` | 主题配置 YAML |
| `pipeline://log` | 流水线日志 |

## 可用 Prompts（3）

`blog_writing` / `tech_analysis` / `blog_idea_generator`

## Docker

```bash
docker build -t droneblog-mcp .
docker run --rm -e DRONEBLOG_DIR=/test-blog -e OPENAI_API_KEY=sk-... droneblog-mcp     # stdio
docker compose up                                                                      # SSE（见 docker-compose.yml）
```

镜像以 `pip install .`（非 editable）安装以验证真实打包，非 root 运行，博客目录在镜像内可写；健康检查为 TCP 连通性探测（不会因 `GET /sse` 挂起）。

## 项目结构

```
droneblog_mcp/
├── pyproject.toml              # 仅打包 src/droneblog_mcp；声明全部运行依赖
├── README.md / USAGE.md
├── src/droneblog_mcp/
│   ├── __init__.py / __main__.py / server.py
│   ├── tools/   setup blog config build pipeline
│   ├── core/    generator pipeline setup deploy
│   ├── models/  config user_config blog
│   └── utils/   fs yaml log github_client
└── tests/                      # pytest：validators / packaging / stdio handshake
```

## 流水线阶段

```
[需求分析] → [Skill 识别] → [AI 生成] → [对话内审阅] → [合规审核] → [安全审查] → [构建验证] → [输出]
```

> 注：旧的“打开 `$EDITOR` 人工审核”已从默认路径移除（MCP stdio 无 TTY）；审阅在客户端对话中完成。
> CLI 交互场景如需本地编辑器，可在 `run_pipeline(..., interactive=True, auto_confirm=False)` 且存在 TTY 时启用。

## 注意事项

1. **Python 版本**：3.11+。
2. **Hexo 依赖**：博客目录需为有效 Hexo 项目（`_config.yml`、`source/_posts/`）。
3. **OpenAI API Key**：仅 `blog_generate` 与 `pipeline_run(task_type="content_creation")` 需要。
4. **GitHub Token**：`setup_init` 需要 `repo`（或 `public_repo`）权限；优先用 `DRONEBLOG_GITHUB_TOKEN` 环境变量，勿用 `--token`（会进进程列表）。
5. **密钥脱敏**：`setup_update_config` 返回值中的 token 已脱敏；`~/.config/droneblog/config.json` 写入后权限收紧为 0600；克隆仓库时 token 通过临时 credential 文件注入，不进 argv。
6. **构建输出**：`build` / `pipeline_run(debug_build)` 现在回传 hexo 的真实输出，便于定位失败原因（不再只返回 “failed”）。
