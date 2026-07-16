# DroneBlog

这是一个基于 [Hexo](https://hexo.io/) 框架搭建的个人博客，通过 [GitHub Pages](https://pages.github.com/) 托管并发布。

- **线上地址**: https://oldoldtea.github.io
- **站点语言**: 简体中文
- **当前主题**: [hexo-theme-kratos-rebirth](https://github.com/Candinya/hexo-theme-kratos-rebirth)（v3.0.1，经 npm 安装）

---

## 🛠 环境依赖

在运行或部署该项目之前，请确保你的开发环境中已安装以下工具：

- **Node.js**: 建议版本 14.x 或更高 (可通过 `node -v` 查看)。当前开发使用 v20.19.4。
- **Git**: 用于博客的源码管理及自动化部署 (可通过 `git --version` 查看)
- **Hexo-CLI**: 建议全局安装 `npm install -g hexo-cli` (用于直接执行 `hexo` 命令)

## 🚀 快速开始

### 1. 安装项目依赖

克隆项目到本地后，在项目根目录下执行：

```bash
npm install
```

### 2. 本地预览

启动本地开发服务器进行实时预览：

```bash
hexo server
# 或者简写为
hexo s
```

> **提示**：若未全局安装 `hexo-cli`，可使用 `npx hexo server` 或 `npm run server`。

### 3. 创建新文章

```bash
hexo new post "我的第一篇文章"
```

新建的文章 Markdown 文件将保存在 `source/_posts/` 目录下。

## 🤖 AI 流水线（Hybrid Pipeline）

本项目内置**混合式 AI 流水线**，用于规范 AI 编程助手的工作流程，确保每次任务执行可追溯、可审计、可回滚。

### 流水线阶段

```
[需求分析] → [Skill 识别] → [执行流程] → [流程合规审核] → [安全审查] → [输出规范]
```

| 阶段 | 职责 |
|------|------|
| **需求分析** | 识别任务类型（内容创作 / 配置调整 / 主题定制 / 问题排查 / 部署发布） |
| **Skill 识别** | 根据技术关键词匹配本地 Skill，未匹配时自动执行 `find-skills` 回退搜索 |
| **执行流程** | 按任务类型执行子流程（如内容创作：Front-matter 校验 → 文件名检查 → 写入 → 构建验证） |
| **流程合规审核** | 验证阶段间信号，检测历史违规，确保无阶段被跳过 |
| **安全审查** | 敏感信息扫描、`.gitignore` 完整性检查、外部链接可信度验证 |
| **输出规范** | 汇总修改摘要、文件清单、验证结果、Skill 匹配结果、后续建议 |

### 流水线配置

| 文件 | 用途 |
|------|------|
| `.ai-skills/pipeline-executor.md` | 执行引擎规范（阶段信号、失败回滚、自检机制） |
| `.ai-skills/pipeline-config.yml` | 声明式配置（阶段定义、检查项、失败策略、输出模板） |
| `.ai-skills/skills-registry.md` | Skill 动态注册表（关键词提取、本地匹配、回退搜索规则） |
| `.ai-pipeline.log` | 执行日志（阶段状态、合规信号、失败记录） |

> 流水线文件位于 `.ai-skills/` 目录，已被 `.gitignore` 排除，不参与版本控制和 Hexo 构建。

---

## 🔌 MCP Server（命令行工具）

本项目已封装为 **MCP (Model Context Protocol) Server**，支持通过 Claude Desktop、Cursor 等 MCP 客户端调用，实现 AI 驱动的博客管理。

### 快速安装

```bash
# 一键配置环境（自动创建 Python 3.11 虚拟环境并安装）
bin/setup-mcp-env.sh

# 激活虚拟环境
source .venv/bin/activate

# 验证安装
droneblog-mcp version
```

### 环境配置

```bash
# 必需
export DRONEBLOG_DIR=/path/to/your/blog
export OPENAI_API_KEY=sk-...

# 可选
export DRONEBLOG_OPENAI_BASE_URL=https://api.openai.com/v1  # 兼容/代理端点
export DRONEBLOG_MODEL=gpt-4o-mini
export DRONEBLOG_TEMPERATURE=0.7
export DRONEBLOG_GITHUB_TOKEN=ghp_...    # GitHub 绑定/自动部署（推荐环境变量，勿用 --token）
```

### 命令行使用

```bash
# 初始化 GitHub 绑定（token 取自 DRONEBLOG_GITHUB_TOKEN 环境变量或交互式输入）
droneblog-mcp setup --mode local   # 本地模式（手动 hexo deploy）
droneblog-mcp setup --mode sync    # 同步归档模式（GitHub Actions 自动部署）
droneblog-mcp status        # 查看流水线状态
droneblog-mcp serve         # 启动 MCP Server（stdio 模式，默认）
droneblog-mcp serve --transport sse --host 0.0.0.0 --port 8765  # 启动 SSE 模式
```

> **安全提示**：请勿使用 `--token` 在命令行明文传入 GitHub Token（会出现在进程列表中）。推荐通过 `DRONEBLOG_GITHUB_TOKEN` 环境变量提供。

### Claude Desktop 配置

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "droneblog": {
      "command": "python3",
      "args": ["-m", "droneblog_mcp"],
      "env": {
        "DRONEBLOG_DIR": "/path/to/your/blog",
        "OPENAI_API_KEY": "sk-..."
      }
    }
  }
}
```

### 可用功能

- **15 个 Tools**: `setup_init`, `setup_status`, `setup_sync_posts`, `setup_update_config`, `blog_generate`, `blog_list`, `blog_read`, `blog_edit`, `blog_delete`, `config_get`, `config_set`, `build`, `deploy`, `pipeline_status`, `pipeline_run`
- **5 个 Resources**: `blog://{slug}`（单篇文章）、`blogs://list`（文章列表）、`config://site`、`config://theme`、`pipeline://log`
- **3 个 Prompts**: `blog_writing`, `tech_analysis`, `blog_idea_generator`

详见 `droneblog_mcp/USAGE.md`

---

---

## 📦 打包与发布

### 常用命令

| 命令 | 说明 |
|------|------|
| `hexo clean` | 清除缓存和 `public/` 目录 |
| `hexo generate` / `hexo g` | 生成静态页面 |
| `hexo deploy` / `hexo d` | 部署到 GitHub Pages |
| `hexo clean && hexo g -d` | 组合命令：清理、生成并直接发布 |

对应 `npm` 脚本：

```bash
npm run server   # hexo server
npm run build    # hexo generate
npm run clean    # hexo clean
npm run deploy   # hexo deploy
```

> **注意**：部署目标仓库为 `oldoldtea.github.io` 的 `master` 分支，与当前源码仓库不同，请勿混淆。

## 📂 目录结构说明

```
my_blog/
├── source/
│   ├── _posts/              # 博客文章（Markdown）
│   ├── category/            # 分类汇总页
│   └── tag/                 # 标签汇总页
├── scaffolds/               # 新建内容模板（post / draft / page）
├── themes/                  # 主题目录（当前为空，主题经 npm 安装）
├── node_modules/
│   └── hexo-theme-kratos-rebirth/  # 当前主题（_config.yml 中 theme: kratos-rebirth）
├── public/                  # 生成的静态站点（hexo generate 输出）
├── .deploy_git/             # 部署临时仓库（hexo-deployer-git 使用）
├── droneblog_mcp/           # MCP Server（AI 驱动的博客管理工具）
│   ├── src/                 # 源码目录
│   ├── dist/                # 构建输出（wheel 包）
│   ├── pyproject.toml       # Python 项目配置
│   ├── README.md            # MCP Server 说明
│   └── USAGE.md             # 使用指南
├── bin/                     # 脚本工具
│   ├── droneblog            # 轻量 CLI wrapper（stdio 调用 MCP Server）
│   ├── droneblog-pipeline.sh  # 已迁移至 bin/droneblog（代理入口，保留兼容）
│   ├── generate-and-archive.sh  # 已弃用，请改用 bin/droneblog 或 MCP 客户端
│   └── setup-mcp-env.sh     # MCP 环境一键配置脚本
├── _config.yml              # 站点核心配置
├── package.json             # 项目依赖与脚本
├── AGENTS.md                # ⬅️ AI 助手工作指南（面向 AI 编程助手）
└── README.md                # 本文件
```

### AI 相关文件

本项目已配置 AI 助手工作流规范，以下文件仅用于 AI 辅助开发，不参与博客构建：

| 文件/目录 | 说明 |
|-----------|------|
| `AGENTS.md` | AI 助手工作指南（流水线、Skill 管理、安全规范等） |
| `.trellis/` | Trellis 工作流规范（任务、spec、标准流程） |
| `.ai-skills/` | AI Skill 存储目录（按需加载的领域知识文件） |
| `.ai-pipeline.log` | AI 流水线执行日志（追加写，记录阶段状态与失败信息） |
| `droneblog_mcp/` | MCP Server 源码（AI 驱动的博客管理工具） |
| `bin/droneblog` | 轻量 CLI wrapper，通过 stdio 调用 MCP Server |
| `bin/setup-mcp-env.sh` | MCP 环境一键配置脚本 |

> `droneblog_mcp/` 源码与 `bin/` 脚本纳入 Git 版本控制；`.ai-skills/` 中仅流水线核心文件（`pipeline-config.yml`、`pipeline-executor.md`、`skills-registry.md`）纳入版本控制，`.ai-pipeline.log`、`.env` 等按 `.gitignore` 排除。

## ✍️ 文章规范（Front-matter）

新建文章时，Markdown 文件头部需包含 YAML Front-matter：

```yaml
---
title: 文章标题
date: 2026-04-14 18:12:46
tags:
  - Kafka
  - 源码解析
categories:
  - 分布式系统
---
```

- `title`: 文章标题（必需）
- `date`: 发布日期，格式 `YYYY-MM-DD HH:mm:ss`
- `tags`: 标签列表
- `categories`: 分类列表

## 🔗 相关资源

- [Hexo 官方文档](https://hexo.io/docs/)
- [Hexo 部署指南](https://hexo.io/docs/one-command-deployment)
- [hexo-theme-kratos-rebirth](https://github.com/Candinya/hexo-theme-kratos-rebirth)

## Star

The easiest way to support developers is to click on the star (⭐) at the top of the page.

<p align="center">
  <a href="https://api.star-history.com/svg?repos=oldoldtea/my_blog">
    <img alt="star" width="50%" src="https://api.star-history.com/svg?repos=oldoldtea/my_blog"/>
  </a>
</p>
