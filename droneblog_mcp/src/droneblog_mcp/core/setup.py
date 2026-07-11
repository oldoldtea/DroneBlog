"""DroneBlog MCP Server - Setup Module"""

import json
import os
import shutil
import stat
import subprocess
import tempfile

from droneblog_mcp.models.user_config import UserConfig, save_user_config
from droneblog_mcp.utils.github_client import GitHubClient
from droneblog_mcp.utils.log import log

# 通过 setup 脚手架新建的“全新项目”默认主题；与本仓库（hexo-theme-maple）无关。
DEFAULT_SCAFFOLD_THEME = "landscape"


class DroneBlogSetup:
    """DroneBlog 初始化器"""

    def __init__(self, config: UserConfig, theme: str = DEFAULT_SCAFFOLD_THEME):
        self.config = config
        self.theme = theme
        self.github = GitHubClient(config.github_token, config.github_username)

    def run_setup(self, mode: str = "local") -> dict:
        """运行初始化设置

        Args:
            mode: "local" | "sync"
        """
        results = {"status": "in_progress", "steps": [], "errors": []}

        # 步骤 1: 验证 GitHub Token
        try:
            verify = self.github.verify_token()
            if not verify["valid"]:
                results["errors"].append(f"GitHub Token 验证失败: {verify.get('error')}")
                results["status"] = "fail"
                return results
            user = verify["user"]
            self.config.github_username = user["login"]
            results["steps"].append(f"✓ GitHub Token 验证通过: {user['login']}")
        except Exception as e:
            results["errors"].append(f"GitHub Token 验证失败: {e}")
            results["status"] = "fail"
            return results

        # 步骤 2: 创建/检查 GitHub Pages 仓库
        pages_repo = self.config.pages_repo_name
        try:
            if not self.github.repo_exists(pages_repo):
                create_result = self.github.create_repo(
                    name=pages_repo,
                    description=f"{self.config.github_username}'s Blog",
                    private=False,
                    auto_init=True,
                )
                if create_result["success"]:
                    results["steps"].append(f"✓ 创建 GitHub Pages 仓库: {pages_repo}")
                else:
                    results["errors"].append(f"创建 Pages 仓库失败: {create_result.get('error')}")
            else:
                results["steps"].append(f"✓ GitHub Pages 仓库已存在: {pages_repo}")
        except Exception as e:
            results["errors"].append(f"检查 Pages 仓库失败: {e}")

        # 步骤 3: 根据模式处理
        if mode == "sync":
            self._setup_sync_mode(results)
        else:
            self._setup_local_mode(results)

        # 步骤 4: 保存配置
        try:
            self.config.sync_mode = mode
            save_user_config(self.config)
            results["steps"].append("✓ 配置已保存到 ~/.config/droneblog/config.json（权限 0600）")
        except Exception as e:
            results["errors"].append(f"保存配置失败: {e}")

        # 最终结果
        if not results["errors"]:
            results["status"] = "success"
            results["message"] = self._get_success_message(mode)
        else:
            results["status"] = "warning"
            results["message"] = "初始化完成，但存在警告"

        return results

    def _setup_sync_mode(self, results: dict):
        """设置同步归档模式"""
        source_repo = self.config.source_repo

        # 创建 Hexo 源码仓库
        try:
            if not self.github.repo_exists(source_repo):
                create_result = self.github.create_repo(
                    name=source_repo,
                    description="Hexo Blog Source",
                    private=False,
                    auto_init=True,
                )
                if create_result["success"]:
                    results["steps"].append(f"✓ 创建 Hexo 源码仓库: {source_repo}")
                    # 初始化 Hexo 项目文件
                    self._init_hexo_project(source_repo)
                    results["steps"].append("✓ 初始化 Hexo 项目文件")
                else:
                    results["errors"].append(f"创建源码仓库失败: {create_result.get('error')}")
            else:
                results["steps"].append(f"✓ Hexo 源码仓库已存在: {source_repo}")
        except Exception as e:
            results["errors"].append(f"设置源码仓库失败: {e}")

        # 克隆到本地
        try:
            self._clone_source_repo()
            results["steps"].append("✓ 源码仓库已克隆到本地")
        except Exception as e:
            results["errors"].append(f"克隆仓库失败: {e}")

    def _setup_local_mode(self, results: dict):
        """设置本地模式"""
        # 初始化本地 Hexo 项目
        try:
            if not self.config.config_file.exists():
                self._init_local_hexo()
                results["steps"].append("✓ 本地 Hexo 项目已初始化")
            else:
                results["steps"].append("✓ 本地 Hexo 项目已存在")
        except Exception as e:
            results["errors"].append(f"初始化本地 Hexo 失败: {e}")

        # 配置 hexo-deployer-git
        try:
            self._setup_deploy_config()
            results["steps"].append("✓ 部署配置已更新")
        except Exception as e:
            results["errors"].append(f"配置部署失败: {e}")

    def _init_hexo_project(self, repo: str):
        """初始化 Hexo 项目文件到仓库"""
        # 创建 _config.yml
        config_content = self._generate_hexo_config()
        self.github.create_or_update_file(
            repo, "_config.yml", config_content, "init: add _config.yml", branch="main"
        )

        # 创建 package.json
        package_content = self._generate_package_json()
        self.github.create_or_update_file(
            repo, "package.json", package_content, "init: add package.json", branch="main"
        )

        # 创建 GitHub Actions 工作流
        workflow_content = self._generate_github_actions_workflow()
        self.github.create_or_update_file(
            repo,
            ".github/workflows/deploy.yml",
            workflow_content,
            "init: add GitHub Actions workflow",
            branch="main",
        )

        # 创建 scaffolds
        for scaffold in ["post.md", "draft.md", "page.md"]:
            content = self._generate_scaffold(scaffold)
            self.github.create_or_update_file(
                repo, f"scaffolds/{scaffold}", content, f"init: add {scaffold}", branch="main"
            )

    def _generate_hexo_config(self) -> str:
        """生成 Hexo 配置文件（仅用于脚手架创建的全新项目）"""
        return f"""# Hexo Configuration
title: {self.config.github_username}'s Blog
subtitle: ''
description: ''
keywords:
author: {self.config.github_username}
language: zh-CN
timezone: Asia/Shanghai

url: https://{self.config.github_username}.github.io
permalink: :year/:month/:day/:title/
permalink_defaults:
pretty_urls:
  trailing_index: true
  trailing_html: true

source_dir: source
public_dir: public
tag_dir: tags
archive_dir: archives
category_dir: categories
code_dir: downloads/code
i18n_dir: :lang
skip_render:

new_post_name: :title.md
default_layout: post
titlecase: false
external_link:
  enable: true
  field: site
  exclude: ''
filename_case: 0
render_drafts: false
post_asset_folder: false
relative_link: false
future: true
syntax_highlighter: highlight.js
highlight:
  line_number: true
  auto_detect: false
  tab_replace: ''
  wrap: true
  hljs: false
prismjs:
  preprocess: true
  line_number: true
  tab_replace: ''

index_generator:
  path: ''
  per_page: 10
  order_by: -date

default_category: uncategorized
category_map:
tag_map:

meta_generator: true

date_format: YYYY-MM-DD
time_format: HH:mm:ss
updated_option: mtime

per_page: 10
pagination_dir: page

include:
exclude:
ignore:

theme: {self.theme}

deploy:
  type: git
  repo: https://github.com/{self.config.github_username}/{self.config.github_username}.github.io.git
  branch: master
  message: "Site updated: {{{{ now('YYYY-MM-DD HH:mm:ss') }}}}"
"""

    def _generate_package_json(self) -> str:
        """生成 package.json"""
        return json.dumps(
            {
                "name": "hexo-site",
                "version": "0.0.0",
                "private": True,
                "scripts": {
                    "build": "hexo generate",
                    "clean": "hexo clean",
                    "deploy": "hexo deploy",
                    "server": "hexo server",
                },
                "hexo": {
                    "version": "7.0.0",
                },
                "dependencies": {
                    "hexo": "^7.0.0",
                    "hexo-generator-archive": "^2.0.0",
                    "hexo-generator-category": "^2.0.0",
                    "hexo-generator-index": "^3.0.0",
                    "hexo-generator-tag": "^2.0.0",
                    "hexo-renderer-ejs": "^2.0.0",
                    "hexo-renderer-marked": "^6.0.0",
                    "hexo-renderer-stylus": "^3.0.0",
                    "hexo-server": "^3.0.0",
                    "hexo-theme-landscape": "^1.0.0",
                },
            },
            indent=2,
            ensure_ascii=False,
        )

    def _generate_github_actions_workflow(self) -> str:
        """生成 GitHub Actions 工作流文件"""
        return """name: Deploy to GitHub Pages

on:
  push:
    branches: [main, master]
  workflow_dispatch:

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Setup Hexo
        run: npm install -g hexo-cli

      - name: Generate static files
        run: |
          hexo clean
          hexo generate

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./public
          publish_branch: master
          external_repository: ${{ github.repository_owner }}/${{ github.repository_owner }}.github.io
"""

    def _generate_scaffold(self, name: str) -> str:
        """生成 scaffold 模板"""
        templates = {
            "post.md": "---\ntitle: {{ title }}\ndate: {{ date }}\ntags:\ncategories:\n---\n",
            "draft.md": "---\ntitle: {{ title }}\ntags:\n---\n",
            "page.md": "---\ntitle: {{ title }}\ndate: {{ date }}\n---\n",
        }
        return templates.get(name, "")

    def _clone_source_repo(self):
        """克隆源码仓库到本地。

        安全：token 通过临时 ``git credential`` 文件（0600）注入，**绝不**出现在
        进程 argv 中（避免 ``ps`` 泄露）。克隆完成后立即删除临时文件。
        """
        target_dir = self.config.dir
        if target_dir.exists() and any(target_dir.iterdir()):
            # 目录已存在且有内容，跳过克隆
            return
        target_dir.mkdir(parents=True, exist_ok=True)

        clone_url = f"https://github.com/{self.config.source_repo_full}.git"
        cred_file = tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8")
        try:
            cred_file.write(
                f"https://{self.config.github_username}:{self.config.github_token}@github.com\n"
            )
            cred_file.close()
            try:
                os.chmod(cred_file.name, stat.S_IRUSR | stat.S_IWUSR)
            except OSError:
                pass

            helper = f"store --file={cred_file.name}"
            subprocess.run(
                [
                    "git",
                    "-c",
                    f"credential.helper={helper}",
                    "clone",
                    clone_url,
                    str(target_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=300,
            )
        finally:
            try:
                os.unlink(cred_file.name)
            except OSError:
                pass

    def _init_local_hexo(self):
        """初始化本地 Hexo 项目（解析 npx 路径，带超时，跨平台）。"""
        npx = shutil.which("npx")
        if not npx:
            raise RuntimeError("未找到 npx：请先安装 Node.js（含 npm）")
        subprocess.run(
            [npx, "hexo", "init", str(self.config.dir)],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
        )

    def _setup_deploy_config(self):
        """配置 hexo-deployer-git"""
        # 修改 _config.yml 中的 deploy 配置
        config_path = self.config.config_file
        if config_path.exists():
            content = config_path.read_text(encoding="utf-8")
            # 确保 deploy 配置正确
            if "deploy:" not in content:
                deploy_config = f"""
deploy:
  type: git
  repo: https://github.com/{self.config.github_username}/{self.config.pages_repo_name}.git
  branch: master
  message: "Site updated: {{{{ now('YYYY-MM-DD HH:mm:ss') }}}}"
"""
                content += deploy_config
                config_path.write_text(content, encoding="utf-8")

    def _get_success_message(self, mode: str) -> str:
        """获取成功消息"""
        lines = [
            f"访问地址: https://{self.config.github_username}.github.io",
        ]
        if mode == "sync":
            lines.append(f"源码仓库: https://github.com/{self.config.source_repo_full}")
        lines.append(f"本地目录: {self.config.dir}")
        return "\n".join(lines)
