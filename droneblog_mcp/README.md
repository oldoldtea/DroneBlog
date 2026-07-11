# DroneBlog MCP Server

> 基于 MCP (Model Context Protocol) 的 DroneBlog AI 辅助博客管理工具。
> 让 Claude Desktop / Cursor 等 MCP 客户端通过标准协议管理 Hexo 博客。

## 功能特性

- **AI 文章生成**：调用 OpenAI 兼容 API 生成技术博客，经过 6 阶段流水线校验
- **文章管理**：列出 / 读取 / 编辑 / 删除
- **配置管理**：读取 / 修改站点与主题配置（支持点号路径）
- **构建部署**：`hexo generate` / `hexo deploy`（跨平台 subprocess，回传真实输出）
- **流水线监控**：查看 6 阶段流水线状态与日志
- **GitHub 绑定（可选）**：初始化 Pages 仓库、本地模式或同步归档模式
- **标准 MCP 传输**：stdio（默认）与 SSE；stdio 下 stdout **仅**承载 JSON-RPC

## 安装

需要 **Python 3.11+**，以及（如需构建/部署）Node.js + Hexo。

### 方式一：一键脚本（推荐）

```bash
bin/setup-mcp-env.sh        # 创建 .venv 并 pip install -e ".[dev]"
source .venv/bin/activate
droneblog-mcp version
```

### 方式二：手动安装

```bash
python3.11 -m venv .venv
source .venv/bin/activate
cd droneblog_mcp
pip install -e ".[dev]"      # 运行依赖在 pyproject 中声明（含 requests）
droneblog-mcp version
```

### 方式三：构建并安装 wheel

```bash
cd droneblog_mcp
python -m build --wheel --outdir dist
pip install dist/droneblog_mcp-0.2.0-py3-none-any.whl
```

> 构建产物（`dist/`、`*.whl`）**不入库**；请本地 `python -m build` 生成。

## 配置

### 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `DRONEBLOG_DIR` | ✅ | 博客工作目录（含 `_config.yml`） |
| `OPENAI_API_KEY` | 生成时必填 | AI 生成所需 |
| `DRONEBLOG_OPENAI_BASE_URL` | 可选 | 兼容/代理端点，默认 `https://api.openai.com/v1` |
| `DRONEBLOG_MODEL` | 可选 | 默认 `gpt-4o-mini` |
| `DRONEBLOG_TEMPERATURE` / `DRONEBLOG_MAX_TOKENS` | 可选 | 采样参数 |
| `DRONEBLOG_GITHUB_TOKEN` | 可选 | GitHub PAT，用于绑定/自动部署（推荐用环境变量，勿用 `--token`） |

也可复制 `.env.example` 为 `.env` 填写（`.env` 已被 `.gitignore` 排除）。

### Claude Desktop 配置

配置文件：
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

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

> stdio 模式下服务默认**完全静默**（stdout 仅供 JSON-RPC）。需要排查时加 `--verbose`，诊断信息会输出到 stderr。

## 命令行

```bash
droneblog-mcp serve                                   # stdio（默认，供 MCP 客户端）
droneblog-mcp serve --transport sse --host 0.0.0.0 --port 8765
droneblog-mcp serve --dir /path/to/blog -v            # 指定目录 + 打印启动横幅到 stderr
droneblog-mcp status                                  # 查看流水线状态（CLI，stdout 输出）
droneblog-mcp setup --mode local                      # 初始化 GitHub 绑定（token 取自环境/交互）
droneblog-mcp version
```

## 可用 Tools（15）

| Tool | 描述 |
|------|------|
| `setup_init` | 初始化 GitHub 绑定（token 可取 `DRONEBLOG_GITHUB_TOKEN`） |
| `setup_status` | 查看绑定状态 |
| `setup_sync_posts` | 同步所有文章到 GitHub（sync 模式） |
| `setup_update_config` | 更新配置（返回值中 token 已脱敏） |
| `blog_generate` | 生成文章（6 阶段流水线；默认 `auto_confirm=true`，草稿经 `draft` 字段回传） |
| `blog_list` | 列出文章（分类/标签/年份筛选） |
| `blog_read` | 读取文章 |
| `blog_edit` | 编辑文章（部分字段更新） |
| `blog_delete` | 删除文章（需 `confirm=true`） |
| `config_get` | 获取站点/主题配置 |
| `config_set` | 修改配置（点号路径） |
| `build` | 构建站点（`clean` 可选，回传真实输出） |
| `deploy` | 部署到 GitHub Pages |
| `pipeline_status` | 流水线状态 |
| `pipeline_run` | 执行完整流水线 |

### `blog_generate` 关键参数

- `slug`：文章文件名（kebab-case，不含 `.md`）。**纯中文 `topic` 必须显式提供 `slug`**，否则无法从标题派生合法 slug，工具会返回清晰错误而不是写出 `source/_posts/.md`。
- `auto_confirm`：默认 `true`——**不会**打开本地编辑器（MCP stdio 无 TTY）。生成的正文通过返回值的 `draft` 字段交还，由客户端在对话中审阅/改写。

## 可用 Resources

| Resource | 描述 |
|----------|------|
| `blog://{slug}` | 单篇文章内容（模板） |
| `blogs://list` | 文章列表（collection，与 `blog://{slug}` 区分，避免路由冲突） |
| `config://site` | 站点配置 |
| `config://theme` | 主题配置 |
| `pipeline://log` | 流水线日志 |

## 可用 Prompts

`blog_writing` / `tech_analysis` / `blog_idea_generator`

## Docker

```bash
docker build -t droneblog-mcp .
# stdio（默认）
docker run --rm -e DRONEBLOG_DIR=/test-blog -e OPENAI_API_KEY=sk-... droneblog-mcp
# SSE（容器内需监听 0.0.0.0）
docker compose up   # 见 docker-compose.yml，已配置可写博客目录与 TCP 健康检查
```

镜像以 `pip install .`（非 editable）安装以验证真实打包，并以非 root 运行；博客目录在镜像内可写。

## 项目结构

```
droneblog_mcp/
├── pyproject.toml              # 打包 src/droneblog_mcp；声明全部依赖
├── README.md / USAGE.md
├── src/droneblog_mcp/
│   ├── __init__.py / __main__.py / server.py
│   ├── tools/  setup blog config build pipeline
│   ├── core/   generator pipeline setup deploy
│   ├── models/ config user_config blog
│   └── utils/  fs yaml log github_client
└── tests/                      # pytest：validators / packaging / stdio handshake
```

## 许可证

MIT
