# DroneBlog MCP Server

> 基于 MCP (Model Context Protocol) 的 DroneBlog AI 辅助博客管理工具

## 功能特性

- **AI 文章生成**：通过 OpenAI API 自动生成技术博客文章，经过完整的 6 阶段流水线验证
- **文章管理**：列出、读取、编辑、删除博客文章
- **配置管理**：获取和修改站点/主题配置
- **构建部署**：执行 hexo clean && hexo generate && hexo deploy
- **流水线监控**：查看 AI 流水线执行状态和日志
- **MCP 协议支持**：兼容 Claude Desktop、Cursor 等 MCP 客户端

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

## 配置

### 环境变量

```bash
export DRONEBLOG_DIR=/path/to/your/blog      # 博客工作目录（必需）
export OPENAI_API_KEY=sk-...                 # OpenAI API Key（必需）
export DRONEBLOG_MODEL=gpt-4o-mini           # 默认模型（可选）
export DRONEBLOG_TEMPERATURE=0.7             # 生成温度（可选）
export DRONEBLOG_MAX_TOKENS=4000             # 最大 token 数（可选）
export DRONEBLOG_AUTO_CONFIRM=false          # 是否跳过人工审核（可选）
```

### Claude Desktop 配置

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`（macOS）或相应配置：

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

### 启动 MCP Server

```bash
# stdio 模式（默认，用于 MCP 客户端如 Claude Desktop）
droneblog-mcp serve

# SSE 模式（HTTP 接口）
droneblog-mcp serve --transport sse

# 指定博客目录
droneblog-mcp serve --dir /path/to/blog
```

### 查看状态

```bash
# 查看流水线状态
droneblog-mcp status
```

## 可用 Tools

| Tool | 描述 |
|------|------|
| `blog_generate` | 生成博客文章（经过 6 阶段流水线） |
| `blog_list` | 列出文章（支持分类/标签/年份筛选） |
| `blog_read` | 读取文章内容 |
| `blog_edit` | 编辑文章 |
| `blog_delete` | 删除文章 |
| `config_get` | 获取站点/主题配置 |
| `config_set` | 修改配置 |
| `build` | 构建站点 |
| `deploy` | 部署到 GitHub Pages |
| `pipeline_status` | 查看流水线状态 |
| `pipeline_run` | 执行完整流水线 |

## 可用 Resources

| Resource | 描述 |
|----------|------|
| `blog://{slug}` | 单篇文章内容 |
| `blog://list` | 文章列表 |
| `config://site` | 站点配置 |
| `config://theme` | 主题配置 |
| `pipeline://log` | 流水线日志 |

## 可用 Prompts

| Prompt | 描述 |
|--------|------|
| `blog_writing` | 博客写作助手 |
| `tech_analysis` | 技术文章分析 |
| `blog_idea_generator` | 博客选题生成 |

## 使用示例

### 生成文章

```
User: 帮我写一篇关于 "C++20 协程" 的博客文章

Claude: [调用 blog_generate]
文章已生成！文件路径: source/_posts/cpp20-coroutines.md
已通过 6 阶段流水线验证，构建成功。
```

### 列出文章

```
User: 列出我最近写的关于 Kafka 的文章

Claude: [调用 blog_list，筛选 tag=Kafka]
找到 2 篇文章...
```

### 构建部署

```
User: 构建并部署站点

Claude: [调用 build，然后调用 deploy]
构建成功！部署成功！
```

## 流水线阶段

```
[需求分析] → [Skill 识别] → [AI 生成] → [人工审核] → [合规审核] → [安全审查] → [构建验证] → [输出]
```

## 项目结构

```
droneblog_mcp/
├── pyproject.toml          # 项目配置
├── README.md
├── src/
│   └── droneblog_mcp/
│       ├── __init__.py
│       ├── __main__.py     # CLI 入口
│       ├── server.py       # MCP Server
│       ├── tools/
│       │   ├── blog.py     # 文章工具
│       │   ├── config.py   # 配置工具
│       │   ├── build.py    # 构建工具
│       │   └── pipeline.py # 流水线工具
│       ├── core/
│       │   ├── generator.py    # AI 生成器
│       │   └── pipeline.py     # 流水线执行器
│       ├── models/
│       │   ├── config.py   # 配置模型
│       │   └── blog.py     # 博客模型
│       └── utils/
│           ├── fs.py       # 文件操作
│           ├── yaml.py     # YAML 处理
│           └── log.py      # 日志工具
```

## 许可证

MIT
