# 牛马日志 (my_blog)

这是一个基于 [Hexo](https://hexo.io/) 框架搭建的个人博客，通过 [GitHub Pages](https://pages.github.com/) 托管并发布。

- **线上地址**: https://oldoldtea.github.io
- **站点语言**: 简体中文
- **当前主题**: [hexo-theme-maple](https://github.com/xbmlz/hexo-theme-maple)

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
├── themes/
│   └── hexo-theme-maple/    # 当前主题目录
├── public/                  # 生成的静态站点（hexo generate 输出）
├── .deploy_git/             # 部署临时仓库（hexo-deployer-git 使用）
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
| `.ai-skills/` | AI Skill 存储目录（按需加载的领域知识文件） |
| `.ai-pipeline.log` | AI 流水线执行日志（追加写，记录阶段状态与失败信息） |

> 以上 AI 相关文件均已被 `.gitignore` 排除，不纳入 Git 版本控制，也不参与 Hexo 静态构建。

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
- [Hexo-Theme-Maple](https://github.com/xbmlz/hexo-theme-maple)

## Star

The easiest way to support developers is to click on the star (⭐) at the top of the page.

<p align="center">
  <a href="https://api.star-history.com/svg?repos=oldoldtea/my_blog">
    <img alt="star" width="50%" src="https://api.star-history.com/svg?repos=oldoldtea/my_blog"/>
  </a>
</p>
