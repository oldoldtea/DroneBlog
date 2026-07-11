"""DroneBlog MCP Server - Setup Tools"""

import os

from mcp.server.fastmcp import FastMCP

from droneblog_mcp.core.setup import DroneBlogSetup
from droneblog_mcp.models.user_config import UserConfig, get_user_config, save_user_config
from droneblog_mcp.utils.log import log


def _resolve_github_token(token: str) -> str:
    """优先使用入参 token，其次回退到环境变量，避免在工具参数/进程 argv 中明文传递。"""
    return (
        (token or "").strip()
        or os.environ.get("DRONEBLOG_GITHUB_TOKEN", "")
        or os.environ.get("GITHUB_TOKEN", "")
    )


def register_setup_tools(mcp: FastMCP) -> None:
    """注册设置相关 Tools"""

    @mcp.tool()
    async def setup_init(token: str = "", mode: str = "local") -> dict:
        """初始化 DroneBlog 配置

        Args:
            token: GitHub Personal Access Token。可留空，留空时回退读取
                   ``DRONEBLOG_GITHUB_TOKEN`` / ``GITHUB_TOKEN`` 环境变量（推荐，避免明文出现在对话中）。
            mode: "local" | "sync" (默认: local)

        Returns:
            包含初始化状态和步骤的字典
        """
        token = _resolve_github_token(token)
        if not token:
            return {
                "status": "fail",
                "message": "未提供 GitHub Token：请传入 token 参数，或设置 DRONEBLOG_GITHUB_TOKEN 环境变量。",
            }
        log("INFO", "setup", f"开始初始化，模式: {mode}")
        config = UserConfig(github_token=token)
        setup = DroneBlogSetup(config)
        result = setup.run_setup(mode)
        return result

    @mcp.tool()
    async def setup_status() -> dict:
        """查看当前配置状态

        Returns:
            包含配置状态和详细信息的字典
        """
        config = get_user_config()
        if not config.is_configured:
            return {
                "status": "unconfigured",
                "message": "DroneBlog 尚未初始化",
                "next_step": "请运行 setup_init 进行初始化",
            }

        # 检查 GitHub 连接状态
        from droneblog_mcp.utils.github_client import GitHubClient
        github = GitHubClient(config.github_token, config.github_username)
        try:
            verify = github.verify_token()
            github_status = "connected" if verify["valid"] else "invalid_token"
            github_user = verify.get("user", {}).get("login", "unknown")
        except Exception as e:
            github_status = "error"
            github_user = str(e)

        return {
            "status": "configured",
            "mode": config.sync_mode,
            "github_user": github_user,
            "github_status": github_status,
            "pages_repo": config.pages_repo_name,
            "source_repo": config.source_repo,
            "local_dir": str(config.dir),
        }

    @mcp.tool()
    async def setup_sync_posts() -> dict:
        """同步所有本地文章到 GitHub（仅同步模式）

        Returns:
            包含同步结果的字典
        """
        from droneblog_mcp.core.deploy import DroneBlogDeployer

        config = get_user_config()
        if not config.is_configured:
            return {
                "status": "fail",
                "message": "DroneBlog 尚未初始化",
            }

        if config.sync_mode != "sync":
            return {
                "status": "fail",
                "message": "仅在同步归档模式下可用",
                "current_mode": config.sync_mode,
            }

        deployer = DroneBlogDeployer(config)
        return deployer.sync_all_posts()

    @mcp.tool()
    async def setup_update_config(
        github_token: str = "",
        github_username: str = "",
        pages_repo: str = "",
        source_repo: str = "",
        sync_mode: str = "",
        auto_deploy: bool = False,
    ) -> dict:
        """更新配置项

        Args:
            github_token: 新的 GitHub Token
            github_username: GitHub 用户名
            pages_repo: Pages 仓库名
            source_repo: 源码仓库名
            sync_mode: "local" | "sync"
            auto_deploy: 是否自动部署

        Returns:
            更新结果
        """
        config = get_user_config()

        if github_token:
            config.github_token = github_token
        if github_username:
            config.github_username = github_username
        if pages_repo:
            config.pages_repo = pages_repo
        if source_repo:
            config.source_repo = source_repo
        if sync_mode:
            config.sync_mode = sync_mode
        config.auto_deploy = auto_deploy

        save_user_config(config)
        return {
            "status": "success",
            "message": "配置已更新",
            "config": config.safe_dump(),
        }
