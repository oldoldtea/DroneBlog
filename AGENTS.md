# AGENTS.md — OldOldTea Blog

> 本文件面向 AI 编程助手。如果你正在阅读此文件，说明你被期望在此 Hexo 博客项目上进行修改、添加内容或排查问题。以下信息均基于项目实际内容，请勿凭假设操作。
>
> ⚠️ **AGENTS.md 保护声明**：
> - **非必要不修改**本文件。它是项目规范的权威来源，随意更改可能导致后续 AI 行为失准。
> - **若确需修改**（如用户明确要求更新流程、添加新规范、修正错误信息），必须先向用户说明修改原因、具体位置和预期影响，**经用户明确同意后方可执行**。
> - **禁止行为**：不得在未经用户确认的情况下，以「优化」、「补充」等理由擅自增删本文件内容。

---

## 项目概览

这是一个基于 [Hexo](https://hexo.io/) 框架搭建的静态博客，站点语言为**简体中文**，使用主题 [hexo-theme-maple](https://github.com/xbmlz/hexo-theme-maple)。

- **站点标题**：牛马日志
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


## Skill 决策规则

1. 首先提取用户动词：
   - 写 / 新建 → write_post
   - 改 / 调整 → config_change
   - 发布 / 部署 → deploy

2. 再根据名词判断是否需要额外 skill：
   - 搜索 / algolia → search_sync
   - 报错 / 失败 → debug_build

3. 如果无法判断：
   - 询问用户确认 skill
   - 不擅自执行


## AI 工作流程（Pipeline）

当用户请求在博客项目上进行操作时，按以下步骤执行。**每个阶段和子任务前均带有 `[ ]` 复选框，AI 执行时应实时更新状态（`[x]` 表示已完成），以便人或 AI 追踪当前进度。**

> **流水线总览**：`[ ] 1. 需求分析 → [ ] 2. Skill 识别 → [ ] 3. 执行流程 → [ ] 4. 安全审查 → [ ] 5. 输出规范`

### 1. 需求分析

- [ ] **阶段完成**：已明确用户意图，归类为以下类型之一：

| 类型 | 说明 | 示例 |
|------|------|------|
| **内容创作** | 新建或修改文章、页面、草稿 | "写一篇关于 Kafka 的文章" |
| **配置调整** | 修改站点或主题配置 | "把每页文章数改成 20" |
| **主题定制** | 修改主题模板、样式、脚本 | "给文章页加个目录" |
| **问题排查** | 构建失败、渲染异常、部署错误 | "hexo generate 报错了" |
| **部署发布** | 构建并推送到 GitHub Pages | "把最新文章发布上线" |

### 2. 知识 Skill 识别与加载

当任务涉及特定领域知识时，自动识别并询问用户是否加载对应 Skill，以提供更专业的输出。

#### Skill 映射表

| 任务场景/关键词 | 推荐 Skill | 说明 |
|----------------|-----------|------|
| React 组件设计、组合模式、props 清理 | `vercel-composition-patterns` | React 组合模式 |
| React/Next.js 性能优化、数据获取、Bundle | `vercel-react-best-practices` | React 最佳实践 |
| React Native、Expo、移动端开发 | `vercel-react-native-skills` | React Native 技能 |
| UI 审查、可访问性检查、UX 规范 | `web-design-guidelines` | Web 设计指南 |
| "找 skill"、"有没有 skill 能..." | `find-skills` | 发现可用 skill |
| 创建新 skill、扩展 AI 能力 | `skill-creator` | Skill 创建指南 |

#### 执行规则

- [ ] **1. 自动识别**：在需求分析阶段，扫描用户请求中的技术关键词和任务类型。
- [ ] **2. 推荐询问**：若匹配到相关 Skill，向用户展示推荐列表并询问：
  > "检测到本次任务涉及 [领域]，推荐加载 Skill：`skill-name`（说明）。是否添加？"
- [ ] **3. 加载执行**：用户确认（或明确指令）后，读取对应 `SKILL.md` 文件，将其中的规范、示例、约束纳入当前工作上下文。
- [ ] **4. 上下文标记**：加载完成后，必须在输出中显式标记：
  ```
  [Skill Loaded: skill-name]
  ```
- [ ] **5. 遵守约束**：后续所有输出必须严格遵守该 Skill 中定义的：
  - [ ] **命名规范**（变量名、函数名、文件命名等）
  - [ ] **结构约束**（代码组织、文件目录、组件拆分规则等）
  - [ ] **禁止事项**（明确不允许的模式、写法或依赖）
- [ ] **6. 冲突解决**：若已加载 Skill 的规范与本项目 `AGENTS.md` 中的规范存在冲突，**以本项目 `AGENTS.md` 为准**。冲突点需在输出中简要说明。
- [ ] **7. 继续工作**：完成上述标记与约束确认后，基于增强的上下文继续执行后续步骤。

> **例外状态**：如用户明确拒绝、未回应，或任务明显不涉及任何 Skill（如纯 Hexo 博客操作），勾选「跳过」：- [ ] 跳过本阶段

---

### 3. 执行流程

#### 内容创作类

- [ ] **1. 确认 Front-matter**：根据 `scaffolds/post.md` 模板，确保包含 `title`、`date`、`tags`/`categories`。
- [ ] **2. 文件名规范**：使用英文或拼音命名 Markdown 文件（如 `kafka-source-analysis.md`），避免中文文件名导致 URL 编码问题。
- [ ] **3. 存放位置**：
  - [ ] 文章 → `source/_posts/`
  - [ ] 草稿 → `source/_drafts/`
  - [ ] 独立页面 → `source/`
- [ ] **4. 内容格式**：遵循 Markdown 规范，代码块标注语言类型，图片使用相对路径或图床链接。
- [ ] **5. 生成本地预览**：执行 `hexo clean && hexo generate && hexo server`，确认渲染正常。

#### 配置调整类

- [ ] **1. 区分配置层级**：
  - [ ] 站点级 → `_config.yml`
  - [ ] 主题级 → `themes/hexo-theme-maple/_config.yml`
- [ ] **2. 修改前备份**：如需大幅改动，先读取当前配置内容，避免误删已有配置。
- [ ] **3. YAML 语法检查**：确保缩进为 2 个空格，不使用 Tab，字符串引号一致。
- [ ] **4. 验证生效**：执行 `hexo clean && hexo generate`，检查控制台是否有配置解析错误。

#### 主题定制类

- [ ] **1. 优先修改主题配置**：检查 `themes/hexo-theme-maple/_config.yml` 是否已有相关开关，避免直接改模板。
- [ ] **2. 确需修改模板时**：
  - [ ] 定位到 `themes/hexo-theme-maple/layout/` 下对应的 EJS 文件
  - [ ] 遵循现有代码风格（2 空格缩进、LF 换行）
  - [ ] 修改后执行 `hexo generate` 验证无渲染错误
- [ ] **3. 样式修改**：编辑 `themes/hexo-theme-maple/source/css/` 下的 Stylus 文件，注意变量命名一致性。

#### 问题排查类

- [ ] **1. 清理缓存**：首先执行 `hexo clean`，排除缓存导致的异常。
- [ ] **2. 查看错误日志**：执行 `hexo generate --debug` 或 `hexo generate 2>&1`，定位具体报错文件与行号。
- [ ] **3. 常见排查点**：
  - [ ] YAML 语法错误（Front-matter 缩进、冒号后空格）
  - [ ] 缺失的依赖包（`npm install` 重新安装）
  - [ ] 主题模板语法错误（EJS 标签未闭合）
  - [ ] 文件权限或路径大小写问题（Linux 环境敏感）
- [ ] **4. 修复后验证**：再次执行 `hexo generate`，确认无报错。

#### 部署发布类

- [ ] **1. 构建前检查**：确认所有修改已保存，无未提交的临时文件。
- [ ] **2. 执行构建**：`hexo clean && hexo generate`
- [ ] **3. 本地预览**（可选）：`hexo server`，快速检查首页和新增页面。
- [ ] **4. 执行部署**：`hexo deploy`，观察推送是否成功。
- [ ] **5. 确认线上**：访问 `https://oldoldtea.github.io` 确认更新已生效。

### 4. 安全审查（必做）

每次修改完成后，自查以下内容：

- [ ] 是否引入了 API Key、密码、Token 等敏感信息？
- [ ] 新增文章中的图片/链接是否指向可信来源？
- [ ] 修改后的配置文件 YAML 语法是否正确？
- [ ] 是否意外修改了 `.gitignore` 导致敏感文件被追踪？

### 5. 输出规范

向用户汇报时，逐项确认并勾选：

- [ ] **1. 修改摘要**：简明说明做了什么改动。
- [ ] **2. 文件清单**：列出新增/修改/删除的文件路径。
- [ ] **3. 验证结果**：`hexo generate` 是否成功，有无警告。
- [ ] **4. 已加载 Skill**：若本次任务加载了额外 Skill，需列出名称及用途。
- [ ] **5. 后续建议**：是否需要部署上线，或进一步调整。

> **注意**：不要代替用户执行 `git commit`、`git push` 或 `hexo deploy`（除非用户明确要求部署）。默认只做到本地验证通过为止。

#### Git 提交规范

若用户明确要求进行 Git 提交，遵守以下规则：

- [ ] **提交工具**：所有 Git 提交操作必须使用 `@command:extension.showGitCommit` 工具执行，不得直接使用 `git commit` 命令。
- [ ] **提交语言**：提交信息（commit message）必须使用**简体汉字**。
- [ ] **分类提交**：按修改内容分类提交，禁止将不相关的改动混在同一个提交中：
  - [ ] `文章`：新增或修改 `source/_posts/` 下的博客文章
  - [ ] `配置`：修改 `_config.yml` 或主题配置文件
  - [ ] `主题`：修改 `themes/hexo-theme-maple/` 下的模板、样式、脚本
  - [ ] `文档`：修改 `README.md`、`AGENTS.md` 等说明文档
  - [ ] `依赖`：修改 `package.json`、更新 npm 依赖包
  - [ ] `修复`：修复构建错误、渲染异常、部署问题等
- [ ] **提交格式**：`[分类] 简述修改内容`
  - 示例：`[文章] 新增 Kafka 源码解析文章`
  - 示例：`[配置] 调整首页分页为每页 20 篇`
  - 示例：`[文档] 更新 README 目录结构说明`

---

### 6. 失败与中断策略

#### 自动失败回滚

- [ ] **触发条件**：同一任务连续失败 ≥ 3 次（如构建报错、文件写入失败、依赖安装失败等）。
  - [ ] **1. 自动中止流水线**：停止后续所有操作。
  - [ ] **2. 输出错误总结**：汇总每次失败的错误信息、尝试的修复措施及失败原因。
  - [ ] **3. 建议人工介入**：向用户说明自动修复已耗尽，建议手动检查环境或提供更多信息。
  - [ ] **4. 写入回滚日志**：将本次流水线的执行进度、失败信息追加写入 `.ai-pipeline.log`。

> **判定标准**：同一子任务（如 `hexo generate`、文件写入、Skill 加载）连续 3 次执行均未成功，即触发回滚。

#### 用户主动中断

- [ ] **Checkpoint 监听**：在任何交互节点（Skill 推荐询问、执行确认、重试询问等），监听用户输入以下指令之一：
  - [ ] `stop`
  - [ ] `abort`
  - [ ] `取消`

- [ ] **立即执行**：确认上述指令后，**立即停止当前任务**，不保存任何中间状态（已写入但未完成的文件保持原状，不自动清理）。

> **Checkpoint 范围**：包括 Skill 加载询问、配置修改确认、构建/部署前的二次确认、以及每次失败后的重试询问。

---

### 7. 回滚日志规范（`.ai-pipeline.log`）

当流水线因失败触发回滚、或被用户主动中断时，必须保留执行痕迹。

#### 存储位置

- [ ] **文件路径**：工作目录根下的隐藏文件 `.ai-pipeline.log`
- [ ] **写入方式**：**追加写（Append-only）**，禁止覆盖或清空历史记录。
- [ ] **Git 隔离**：已被 `.gitignore` 排除，**不参与版本控制**。

#### 日志格式

每条记录以行为单位，包含以下字段：

```
[YYYY-MM-DDTHH:mm:ss+08:00] [STATUS] [STAGE] 详细描述
```

- **STATUS**：`START` / `OK` / `FAIL` / `ROLLBACK` / `ABORT`
- **STAGE**：当前流水线阶段名（如 `需求分析` / `Skill加载` / `内容创作` / `部署发布`）
- **详细描述**：失败原因、异常堆栈、尝试过的修复措施、建议的人工介入方向。

#### 记录时机

- [ ] **阶段开始时**：记录 `[START] [阶段名] Pipeline started for task: xxx`
- [ ] **阶段成功时**：记录 `[OK] [阶段名] 简述成果`
- [ ] **阶段失败时**：记录 `[FAIL] [阶段名] 错误信息 + 已尝试次数`
- [ ] **触发回滚时**：记录 `[ROLLBACK] [阶段名] 连续失败≥3次，中止流水线。错误汇总：...`
- [ ] **用户中断时**：记录 `[ABORT] [阶段名] 用户输入 stop/abort/取消，任务中断。`

> **示例**：
> ```
> [2026-05-12T16:30:00+08:00] [START] [内容创作] Pipeline started for task: 写一篇关于 Kafka 的文章
> [2026-05-12T16:30:05+08:00] [OK] [需求分析] 归类为内容创作类
> [2026-05-12T16:30:06+08:00] [OK] [Skill加载] 无匹配Skill，跳过
> [2026-05-12T16:31:00+08:00] [FAIL] [内容创作] hexo generate 报错：YAMLException: bad indentation
> [2026-05-12T16:31:30+08:00] [FAIL] [内容创作] 重试1：修复缩进后仍报错
> [2026-05-12T16:32:00+08:00] [FAIL] [内容创作] 重试2：替换模板后仍报错
> [2026-05-12T16:32:01+08:00] [ROLLBACK] [内容创作] 连续失败≥3次，中止流水线。
> ```

---

### 8. Skill 存储规范

#### 目录结构

- [ ] **存储路径**：项目根目录下的 `.ai-skills/`
- [ ] **文件命名**：每个 Skill 一个独立文件，文件名即 Skill 名称，使用 kebab-case：
  ```
  .ai-skills/
  ├── vercel-react-best-practices.md
  ├── web-design-guidelines.md
  └── custom-skill-name.md
  ```

#### 加载规则

- [ ] **单文件 = 单 Skill**：禁止在一个 `.md` 文件中定义多个 Skill。
- [ ] **多 Skill 并行**：允许同时加载多个 Skill，加载顺序按用户确认或文件名字母序。
- [ ] **冲突处理**：多个 Skill 之间若存在冲突，以最后被加载的 Skill 为准；若与 `AGENTS.md` 冲突，始终以 `AGENTS.md` 为准。

#### 构建隔离

- [ ] **Git 隔离**：`.ai-skills/` 目录已被 `.gitignore` 排除，**不参与 Git 版本控制**。
- [ ] **构建隔离**：`.ai-skills/` 目录不在 Hexo 的 `source/` 或 `themes/` 路径下，**不参与静态站点构建**，不会出现在生成的 `public/` 中。
