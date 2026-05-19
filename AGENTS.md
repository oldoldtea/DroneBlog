# AGENTS.md — DroneBlog

> 本文件面向 AI 编程助手。如果你正在阅读此文件，说明你被期望在此 Hexo 博客项目上进行修改、添加内容或排查问题。以下信息均基于项目实际内容，请勿凭假设操作。
>
> ⚠️ **AGENTS.md 保护声明**：
> - **非必要不修改**本文件。它是项目规范的权威来源，随意更改可能导致后续 AI 行为失准。
> - **若确需修改**（如用户明确要求更新流程、添加新规范、修正错误信息），必须先向用户说明修改原因、具体位置和预期影响，**经用户明确同意后方可执行**。
> - **禁止行为**：不得在未经用户确认的情况下，以「优化」、「补充」等理由擅自增删本文件内容。

---

## 项目概览

这是一个基于 [Hexo](https://hexo.io/) 框架搭建的静态博客，站点语言为**简体中文**，使用主题 [hexo-theme-maple](https://github.com/xbmlz/hexo-theme-maple)。

- **站点标题**：DroneBlog
- **作者**：OldOldTea
- **部署目标**：GitHub Pages (`https://oldoldtea.github.io`)
- **Hexo 版本**：`8.1.1`
- **Node.js 要求**：建议 14.x 或更高（实际开发使用 v20.19.4）

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 静态站点生成器 | Hexo `^8.0.0` |
| 模板引擎 | EJS (`hexo-renderer-ejs`) |
| CSS 预处理器 | Stylus (`hexo-renderer-stylus`) |
| Markdown 渲染 | `hexo-renderer-marked` + `hexo-renderer-multi-markdown-it` |
| 主题 | `hexo-theme-maple`（本地子目录，非 npm 包） |
| 部署 | `hexo-deployer-git` → GitHub Pages |
| 搜索 | Algolia (`hexo-algoliasearch`) |
| RSS 订阅 | `hexo-generator-feed` (Atom 格式) |
| 代码高亮 | highlight.js |

---

## 目录结构

```
my_blog/
├── _config.yml              # 站点核心配置（站点信息、URL、部署、Feed 等）
├── package.json             # 项目依赖与 npm 脚本
├── scaffolds/               # 新建内容模板
│   ├── post.md              # 文章模板
│   ├── draft.md             # 草稿模板
│   └── page.md              # 独立页面模板
├── source/                  # 源文件目录
│   ├── _posts/              # 博客文章（Markdown）
│   ├── category/
│   │   └── index.md         # 分类汇总页（layout: category）
│   └── tag/
│       └── index.md         # 标签汇总页（layout: tag）
├── themes/
│   └── hexo-theme-maple/    # 当前使用的主题（完整主题目录）
│       ├── _config.yml      # 主题配置（导航、分析、插件开关等）
│       ├── layout/          # EJS 模板
│       ├── source/          # 主题静态资源（CSS、JS、图片）
│       └── scripts/         # 主题辅助脚本（echarts、mermaid、wordcount）
├── public/                  # 生成的静态站点（hexo generate 输出，.gitignore 忽略）
└── .deploy_git/             # 部署时 hexo-deployer-git 使用的临时仓库
```

---

## 常用命令

所有命令均在项目根目录执行。

### 安装依赖

```bash
npm install
```

> 项目中同时存在 `package-lock.json`、`pnpm-lock.yaml` 和 `yarn.lock`，但默认使用 npm。

### 本地开发预览

```bash
hexo server        # 或 hexo s
# 未全局安装 hexo-cli 时可用：
npx hexo server
npm run server
```

### 内容创建

```bash
hexo new post "文章标题"     # 在 source/_posts/ 下创建新文章
hexo new draft "草稿标题"    # 在 source/_drafts/ 下创建草稿
hexo new page "页面标题"     # 在 source/ 下创建独立页面
```

### 构建与部署

```bash
hexo clean                    # 清除缓存和 public/ 目录
hexo generate                 # 生成静态页面（或 hexo g）
hexo deploy                   # 部署到 GitHub Pages（或 hexo d）

# 组合命令（最常用）
hexo clean && hexo generate && hexo deploy
hexo clean && hexo g -d
```

对应的 npm 脚本：

- `npm run build` → `hexo generate`
- `npm run clean` → `hexo clean`
- `npm run deploy` → `hexo deploy`
- `npm run server` → `hexo server`

---

## 内容规范（Front-matter）

文章和页面使用 YAML Front-matter。实际项目中观察到的常用字段：

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

**规范说明**：

- `title`：文章标题（必需）。
- `date`：发布日期，格式 `YYYY-MM-DD HH:mm:ss`。Hexo 默认按此字段倒序排列。
- `tags`：标签列表，支持多标签。项目中有部分文章仅用 `tags`，部分仅用 `categories`，也有两者混用。
- `categories`：分类列表。项目中的文章常使用 `categories` 替代或补充 `tags`。

**模板文件**（`scaffolds/`）定义了新建内容的默认 Front-matter：

- `post.md`：包含 `title`、`date`、`tags`
- `draft.md`：包含 `title`、`tags`（无 `date`）
- `page.md`：包含 `title`、`date`

> 提示：如需修改新建文章的默认模板，直接编辑 `scaffolds/post.md` 即可。

---

## 站点配置要点（`_config.yml`）

以下是与日常维护密切相关的配置项：

- **语言**：`language: zh-CN`
- **时区**：`timezone: 'Asia/Shanghai'`
- **URL**：`url: https://oldoldtea.github.io`
- **永久链接**：`permalink: :year/:month/:day/:title/`
- **分页**：首页及归档每页 10 篇文章
- **代码高亮**：`syntax_highlighter: highlight.js`，行号开启
- **主题**：`theme: hexo-theme-maple`
- **部署**：
  ```yaml
  deploy:
    type: git
    repo: https://github.com/oldoldtea/oldoldtea.github.io.git
    branch: master
    message: "Site updated: {{ now('YYYY-MM-DD HH:mm:ss') }}"
  ```
- **RSS Feed**：Atom 格式，路径 `atom.xml`，限制 20 条，含全文内容

---

## 主题配置（`themes/hexo-theme-maple/_config.yml`）

主题 `hexo-theme-maple` 的主要功能开关：

- **导航**：`nav` 定义顶部菜单（Posts → `/archives`, Categories → `/category`, Tags → `/tag`）
- **Favicon / Logo**：分别指向 `/favicon.png` 和 `/images/logo.svg`
- **社交链接**：`links` 中配置了 GitHub 链接
- **分析**：`google_analytics` / `baidu_analytics`（目前为空）
- **功能插件**：
  - `fancybox: true` — 图片灯箱
  - `mathjax: true` — 数学公式渲染
  - `echarts: true` — 图表支持
  - `mermaid: true` — 流程图支持
  - `busuanzi: true` — 不蒜子访问统计
  - `giscus` — 评论系统（目前未配置）
- **特效**：`maple` 配置枫叶飘落动画（`enable: true`, `count: 10`, `speed: 0.5`）

> 如需调整主题外观或功能，修改 `themes/hexo-theme-maple/_config.yml`，**不要**直接修改主题目录内的模板文件（除非确需定制主题行为）。

---

## 代码风格

项目根目录下无 `.editorconfig`，但主题目录下存在：

```ini
root = true
[*]
charset = utf-8
indent_style = space
indent_size = 2
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
```

**建议在整个项目中遵循**：

- 缩进：2 个空格（Soft tab）
- 换行：LF (`\n`)
- 编码：UTF-8
- Markdown 文件：保留末尾换行符，去除行尾空格

---

## 部署流程

1. 本地编辑 Markdown 源文件或配置。
2. 执行 `hexo clean && hexo generate` 重新生成静态页面。
3. 执行 `hexo deploy`，`hexo-deployer-git` 会将 `public/` 内容推送到远程仓库 `oldoldtea.github.io` 的 `master` 分支。
4. GitHub Pages 自动发布该分支内容。

> `.deploy_git/` 是 hexo-deployer-git 的本地临时仓库，已被 `.gitignore` 忽略，无需手动管理。

---

## 测试策略

本项目为静态博客，**无自动化测试套件**。验证方式以人工为主：

- `hexo server` 本地预览，检查排版、链接、图片、代码块渲染是否正常。
- `hexo generate` 后查看终端是否有渲染错误或缺失资源警告。
- 部署后访问线上地址确认最终效果。

---

## 安全与注意事项

- **不要将敏感信息写入 `_config.yml` 或文章中**：`_config.yml` 和 Markdown 源文件均在 Git 仓库中管理，公开可见。
- **Algolia 搜索**：如开启 `hexo-algoliasearch`，需妥善保管 Algolia Admin API Key，避免硬编码在配置中提交到仓库。
- **部署仓库分离**：博客源码仓库是 `my_blog`，部署目标是 `oldoldtea.github.io`，两者不同，请勿混淆。
- **缓存问题**：Hexo 偶尔会缓存旧数据，遇到生成异常时优先执行 `hexo clean`。

---

## 扩展依赖清单（`package.json`）

除 Hexo 核心外，项目还依赖以下插件：

- `hexo-algoliasearch` — Algolia 搜索集成
- `hexo-autoprefixer` — CSS Autoprefixer
- `hexo-deployer-git` — Git 部署
- `hexo-generator-archive` / `category` / `index` / `tag` — 各类索引页生成
- `hexo-generator-feed` — RSS/Atom Feed
- `hexo-renderer-ejs` / `marked` / `multi-markdown-it` / `stylus` — 渲染器
- `hexo-server` — 本地开发服务器
- `hexo-symbols-count-time` — 阅读时长与字数统计
- `hexo-theme-kratos-rebirth` / `hexo-theme-landscape` — 其他主题（作为依赖安装，但当前未使用）

---

## 给 AI 助手的快速检查清单

在对本项目进行修改前，请确认：

1. [ ] 是否需要在 `source/_posts/` 下新增 Markdown 文件？
2. [ ] 是否需要修改 `_config.yml`（站点级）或 `themes/hexo-theme-maple/_config.yml`（主题级）？
3. [ ] 执行 `hexo clean && hexo generate` 是否能正常构建？
4. [ ] 新增内容是否包含正确的 Front-matter（`title`、`date`、`tags`/`categories`）？
5. [ ] 是否无意中将敏感信息提交到了 Git 仓库？

---

## AI 工作流入口

> 本项目采用**混合式流水线（Hybrid Pipeline）**架构。AI 执行任务的完整流程由以下文件协同驱动：

### 加载顺序

```
AGENTS.md
  → .ai-skills/pipeline-executor.md  （执行引擎规范）
    → .ai-skills/pipeline-config.yml   （声明式流水线配置）
      → .ai-skills/skills-registry.md  （Skill 注册表，按需）
```

### 文件职责

| 文件 | 职责 | 修改频率 |
|------|------|----------|
| `AGENTS.md` | 项目知识、技术栈、目录结构、常用命令 | 低 |
| `.ai-skills/pipeline-executor.md` | 执行引擎接口、日志规范、失败回滚触发器 | 极低 |
| `.ai-skills/pipeline-config.yml` | 流水线阶段定义、检查项、输出模板、失败策略 | 中 |
| `.ai-skills/skills-registry.md` | Skill 映射表、加载规则 | 中 |
| `.githooks/*` | 本地 Git Hooks（提交/推送前校验） | 低 |

### 关键规则

- **不要代替用户执行 `git commit`、`git push` 或 `hexo deploy`**（除非用户明确要求部署）。默认只做到本地验证通过为止。
- **所有 Git 提交操作必须使用 `@command:extension.showGitCommit` 工具执行**，不得直接使用 `git commit` 命令。
- **提交信息必须使用简体汉字**，格式：`[分类] 简述修改内容`
  - 示例：`[文章] 新增 Kafka 源码解析文章`
  - 示例：`[配置] 调整首页分页为每页 20 篇`

### 流水线总览

```
[ ] 1. 需求分析 → [ ] 2. Skill 识别 → [ ] 3. 执行流程 → [ ] 4. 安全审查 → [ ] 5. 输出规范
```

各阶段的详细规则、检查项和失败策略定义在 `.ai-skills/pipeline-config.yml` 中。AI 应在读取本文件后，按该配置驱动执行。
