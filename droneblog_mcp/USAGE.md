# DroneBlog MCP Server 使用指南

## 打包

### 方式一：Wheel 包（推荐）

```bash
cd droneblog_mcp

# 使用虚拟环境的 Python 3.11 打包
source ../.venv/bin/activate
python -m build
```

输出：
- `dist/droneblog_mcp-0.1.0-py3-none-any.whl` — 可直接安装的 wheel 包
- `dist/droneblog_mcp-0.1.0.tar.gz` — 源码分发包

> **注意**：系统 Python 3.8 缺少 `ensurepip`，无法直接运行 `python3 -m build`。请使用 `.venv`（Python 3.11）中的 `python`。

### 方式二：本地开发模式

```bash
cd droneblog_mcp

# 使用虚拟环境
source ../.venv/bin/activate
pip install -e .
```

## 安装

### 方式一：一键配置（推荐）

项目根目录提供了自动配置脚本，一键创建 Python 3.11 虚拟环境并安装 MCP Server：

```bash
# 在项目根目录执行
bin/setup-mcp-env.sh

# 激活虚拟环境
source .venv/bin/activate

# 验证安装
droneblog-mcp version
```

### 方式二：手动安装

```bash
# 创建 Python 3.11 虚拟环境
python3.11 -m venv .venv
source .venv/bin/activate

# 安装 MCP Server（开发模式）
cd droneblog_mcp
pip install -e .

# 验证
droneblog-mcp version
```

### 方式三：从 Wheel 包安装

```bash
# 安装已构建的 wheel 包
pip install droneblog_mcp/dist/droneblog_mcp-0.1.0-py3-none-any.whl
```

### 方式四：打包（开发者）

```bash
cd droneblog_mcp

# 使用虚拟环境的 Python 打包
source ../.venv/bin/activate
python -m build

# 输出：
# dist/droneblog_mcp-0.1.0-py3-none-any.whl
# dist/droneblog_mcp-0.1.0.tar.gz
```

## 配置

### 环境变量

```bash
export DRONEBLOG_DIR=/path/to/your/blog      # 博客工作目录（必需）
export OPENAI_API_KEY=sk-...                 # OpenAI API Key（必需，用于 AI 生成）
export DRONEBLOG_MODEL=gpt-4o-mini           # 默认 AI 模型（可选）
export DRONEBLOG_TEMPERATURE=0.7             # 生成温度（可选）
export DRONEBLOG_MAX_TOKENS=4000             # 最大 token 数（可选）
export DRONEBLOG_AUTO_CONFIRM=false          # 是否跳过人工审核（可选，默认 false）
```

### MCP 客户端配置（Claude Desktop）

编辑配置文件：
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "droneblog": {
      "command": "python3",
      "args": ["-m", "droneblog_mcp"],
      "env": {
        "DRONEBLOG_DIR": "/home/lz/workspace/personal/my_blog",
        "OPENAI_API_KEY": "sk-..."
      }
    }
  }
}
```

## 命令行使用

### 查看版本

```bash
droneblog-mcp version
```

### 初始化 GitHub 绑定

```bash
# 本地模式（手动 hexo deploy）
droneblog-mcp setup --token ghp_xxx --mode local

# 同步归档模式（GitHub Actions 自动部署）
droneblog-mcp setup --token ghp_xxx --mode sync
```

### 查看状态

```bash
# 使用环境变量指定博客目录
export DRONEBLOG_DIR=/path/to/blog
droneblog-mcp status

# 或临时指定
DRONEBLOG_DIR=/path/to/blog droneblog-mcp status
```

### 启动 MCP Server

```bash
# stdio 模式（默认，用于 MCP 客户端如 Claude Desktop）
droneblog-mcp serve

# SSE 模式（HTTP 接口）
droneblog-mcp serve --transport sse

# 指定博客目录
droneblog-mcp serve --dir /path/to/blog
```

## 可用 Tools（15 个）

| Tool | 功能 | 示例参数 |
|------|------|----------|
| `setup_init` | 初始化 GitHub 绑定 | `{"token": "ghp_xxx", "mode": "local"}` |
| `setup_status` | 查看绑定状态 | `{}` |
| `setup_sync_posts` | 同步文章到 GitHub | `{}` |
| `setup_update_config` | 更新配置 | `{"github_token": "ghp_xxx", "sync_mode": "sync"}` |
| `blog_generate` | 生成博客文章 | `{"topic": "C++20 协程", "category": "系统编程", "tags": ["C++", "协程", "异步编程"], "auto_deploy": false}` |
| `blog_list` | 列出文章 | `{"category": "后端开发", "limit": 10}` |
| `blog_read` | 读取文章 | `{"slug": "tokio-async-runtime"}` |
| `blog_edit` | 编辑文章 | `{"slug": "xxx", "title": "新标题", "tags": ["新标签1", "新标签2"]}` |
| `blog_delete` | 删除文章 | `{"slug": "xxx", "confirm": true}` |
| `config_get` | 获取配置 | `{"scope": "site"}` |
| `config_set` | 修改配置 | `{"scope": "site", "key": "title", "value": "新标题"}` |
| `build` | 构建站点 | `{}` |
| `deploy` | 部署站点 | `{"build_first": true}` |
| `pipeline_status` | 查看流水线状态 | `{}` |
| `pipeline_run` | 执行完整流水线 | `{"task_type": "debug_build", "params": {}}` |

## 可用 Resources（5 个）

| Resource | 内容 |
|----------|------|
| `blog://{slug}` | 单篇文章 Markdown 内容 |
| `blog://list` | 文章列表 |
| `config://site` | 站点配置 YAML |
| `config://theme` | 主题配置 YAML |
| `pipeline://log` | 流水线日志 |

## 可用 Prompts（3 个）

| Prompt | 用途 |
|--------|------|
| `blog_writing` | 博客写作助手 |
| `tech_analysis` | 技术文章分析 |
| `blog_idea_generator` | 博客选题生成 |

## 使用示例

### 生成文章

```
User: 帮我写一篇关于 "C++20 协程" 的博客文章，分类到系统编程，标签是 C++、协程、异步编程

Claude: [调用 blog_generate 工具]

文章已生成！文件路径: source/_posts/cpp20-coroutines.md
标题: C++20 协程深度解析
分类: 系统编程
标签: C++, 协程, 异步编程
已通过 6 阶段流水线验证，构建成功。
```

### 列出文章

```
User: 列出我最近写的关于 Kafka 的文章

Claude: [调用 blog_list 工具，筛选 tag=Kafka]

找到 2 篇文章:
1. kafka-message-transmission (Kafka 消息传输机制)
2. kafka-source-analysis (Kafka 源码解析)
```

### 构建部署

```
User: 构建并部署站点

Claude: [调用 build 工具，然后调用 deploy 工具]

构建成功！public/ 目录已生成。
部署成功！已推送到 oldoldtea.github.io 的 master 分支。
```

## 项目结构

```
droneblog_mcp/
├── pyproject.toml              # 项目配置
├── README.md
├── src/
│   └── droneblog_mcp/
│       ├── __init__.py
│       ├── __main__.py         # CLI 入口
│       ├── server.py           # MCP Server 主类
│       ├── tools/
│       │   ├── setup.py        # GitHub 绑定工具
│       │   ├── blog.py         # 文章相关工具
│       │   ├── config.py       # 配置相关工具
│       │   ├── build.py        # 构建部署工具
│       │   └── pipeline.py     # 流水线工具
│       ├── core/
│       │   ├── setup.py        # 初始化逻辑
│       │   ├── deploy.py       # 部署逻辑
│       │   ├── pipeline.py     # 流水线执行器
│       │   └── generator.py    # AI 内容生成器
│       ├── models/
│       │   ├── config.py       # Pydantic 配置模型
│       │   ├── user_config.py  # 用户 GitHub 配置
│       │   └── blog.py         # 博客数据模型
│       └── utils/
│           ├── github_client.py # GitHub API 客户端
│           ├── fs.py           # 文件系统操作
│           ├── yaml.py         # YAML 处理
│           └── log.py          # 日志工具
├── dist/                       # 构建输出
│   ├── droneblog_mcp-0.1.0-py3-none-any.whl
│   └── droneblog_mcp-0.1.0.tar.gz
└── tests/                      # 测试目录
```

## 流水线阶段

```
[需求分析] → [Skill 识别] → [AI 生成] → [人工审核] → [合规审核] → [安全审查] → [构建验证] → [输出]
```

## 注意事项

1. **Python 版本**: 需要 Python 3.11+
2. **Hexo 依赖**: 博客目录必须包含有效的 Hexo 项目（`_config.yml`、`source/_posts/` 等）
3. **OpenAI API Key**: 只有 `blog_generate` 和 `pipeline_run` 的 `content_creation` 任务需要
4. **GitHub Token**: `setup_init` 需要 GitHub Personal Access Token（需要 `repo` 或 `public_repo` 权限）
5. **人工审核**: 默认会打开编辑器让用户审核生成的文章，可通过 `auto_confirm=true` 跳过（仅用于自动化场景）
6. **自动部署**: `blog_generate` 支持 `auto_deploy=true` 参数，根据配置的模式自动部署（local 模式执行 `hexo deploy`，sync 模式提交到 GitHub 触发 Actions）
7. **Git 提交**: 部署前确保已配置 `hexo-deployer-git`（local 模式）或已初始化 GitHub 绑定（sync 模式）
