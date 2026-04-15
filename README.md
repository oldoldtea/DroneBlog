# my_blog

这是一个基于 [Hexo](https://hexo.io/) 框架搭建的个人博客，通过 [GitHub Pages](https://pages.github.com/) 托管并发布。

## 🛠 环境依赖

在运行或部署该项目之前，请确保你的开发环境中已安装以下工具：

- **Node.js**: 建议版本 14.x 或更高 (可通过 `node -v` 查看)，这里我使用的版本是v20.19.4
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

### 1. 清理缓存

建议在重新生成静态页面前执行，以避免旧缓存导致的问题：

```bash
hexo clean
```

### 2. 生成静态页面

将 Markdown 源文件编译为 HTML 静态页面：

```bash
hexo generate
# 或者简写为
hexo g
```

### 3. 部署到 GitHub Pages

一键将生成的静态页面发布到你在 `_config.yml` 中配置的 GitHub 仓库：

```bash
hexo deploy
# 或者简写为
hexo d
```

> **进阶技巧**：你可以组合执行指令，如 `hexo clean && hexo g -d` (清理、生成并直接发布)。

## 📂 目录结构说明

- `source/_posts/`: 存放所有博客文章的 Markdown 源文件
- `themes/`: 存放博客主题（当前正在使用: [hexo-theme-maple](https://github.com/subat0m/hexo-theme-maple)）
- `public/`: 打包后生成的静态文件目录（部署时会推送此文件夹内容）
- `_config.yml`: 博客的核心配置文件（包含站点信息、部署配置等）
- `package.json`: 定义了项目依赖及快捷脚本

## 🔗 相关资源

- [Hexo 官方文档](https://hexo.io/docs/)
- [Hexo 部署指南](https://hexo.io/docs/one-command-deployment)
- [Hexo-Theme-Maple 官方说明](https://github.com/subat0m/hexo-theme-maple)
