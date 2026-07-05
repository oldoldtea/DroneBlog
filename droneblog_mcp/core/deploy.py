"""DroneBlog MCP Server - Deploy Module"""

from pathlib import Path

from droneblog_mcp.models.user_config import UserConfig, get_user_config
from droneblog_mcp.utils.fs import hexo_deploy, write_post
from droneblog_mcp.utils.github_client import GitHubClient
from droneblog_mcp.utils.log import log


class DroneBlogDeployer:
    """DroneBlog 部署器"""

    def __init__(self, config: UserConfig):
        self.config = config
        self.github = GitHubClient(config.github_token, config.github_username)

    def deploy_article(self, slug: str, content: str) -> dict:
        """部署单篇文章

        根据 sync_mode 选择部署路径：
        - local: 写入本地，用户手动 hexo deploy
        - sync: 提交到 GitHub，触发 Actions 自动部署
        """
        if self.config.sync_mode == "sync":
            return self._deploy_to_github(slug, content)
        else:
            return self._deploy_local(slug, content)

    def _deploy_to_github(self, slug: str, content: str) -> dict:
        """同步归档模式：提交到 GitHub"""
        repo = self.config.source_repo
        path = f"source/_posts/{slug}.md"

        try:
            result = self.github.create_or_update_file(
                repo=repo,
                path=path,
                content=content,
                message=f"[文章] 新增 {slug}",
                branch="main",
            )
            if result["success"]:
                log("OK", "deploy", f"文章已提交到 GitHub: {repo}/{path}")
                return {
                    "status": "success",
                    "message": f"文章已提交到 {repo}/{path}",
                    "url": f"https://github.com/{self.config.source_repo_full}/blob/main/{path}",
                    "note": "GitHub Actions 将自动构建并部署",
                }
            else:
                log("FAIL", "deploy", f"提交失败: {result.get('error')}")
                return {
                    "status": "fail",
                    "message": f"提交失败: {result.get('error')}",
                }
        except Exception as e:
            log("FAIL", "deploy", f"提交异常: {e}")
            return {"status": "fail", "message": str(e)}

    def _deploy_local(self, slug: str, content: str) -> dict:
        """本地模式：写入本地文件并执行 hexo deploy"""
        try:
            file_path = write_post(slug, content)
            log("OK", "deploy", f"文章已保存到本地: {file_path}")

            # 尝试自动执行 hexo deploy
            deploy_ok, deploy_msg = hexo_deploy()
            if deploy_ok:
                log("OK", "deploy", "hexo deploy 成功")
                return {
                    "status": "success",
                    "message": f"文章已保存并部署: {file_path}",
                    "deploy_output": deploy_msg,
                }
            else:
                log("WARN", "deploy", f"hexo deploy 失败: {deploy_msg}")
                return {
                    "status": "warning",
                    "message": f"文章已保存到 {file_path}",
                    "warning": f"hexo deploy 失败: {deploy_msg}",
                    "next_step": "请手动运行 'hexo deploy' 部署",
                }
        except Exception as e:
            log("FAIL", "deploy", f"本地部署异常: {e}")
            return {"status": "fail", "message": str(e)}

    def sync_all_posts(self) -> dict:
        """同步所有本地文章到 GitHub（用于首次启用同步模式）"""
        if self.config.sync_mode != "sync":
            return {"status": "fail", "message": "仅在同步归档模式下可用"}

        posts_dir = self.config.posts_dir
        if not posts_dir.exists():
            return {"status": "fail", "message": "本地文章目录不存在"}

        synced = 0
        failed = 0

        for md_file in posts_dir.glob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                result = self.github.create_or_update_file(
                    repo=self.config.source_repo,
                    path=f"source/_posts/{md_file.name}",
                    content=content,
                    message=f"[同步] {md_file.stem}",
                    branch="main",
                )
                if result["success"]:
                    synced += 1
                else:
                    failed += 1
            except Exception as e:
                failed += 1
                log("FAIL", "deploy", f"同步 {md_file.name} 失败: {e}")

        log("OK", "deploy", f"同步完成: {synced} 成功, {failed} 失败")
        return {
            "status": "success" if failed == 0 else "warning",
            "message": f"已同步 {synced} 篇文章到 GitHub" + (f", {failed} 失败" if failed > 0 else ""),
            "synced": synced,
            "failed": failed,
        }


def auto_deploy_article(slug: str, content: str) -> dict:
    """自动部署文章（根据当前配置的模式）"""
    config = get_user_config()
    if not config.is_configured:
        return {
            "status": "skip",
            "message": "GitHub 未配置，跳过自动部署",
            "note": "请运行 'droneblog-mcp setup' 进行初始化",
        }

    deployer = DroneBlogDeployer(config)
    return deployer.deploy_article(slug, content)
