"""DroneBlog MCP Server - Build & Deploy Tools"""

from mcp.server.fastmcp import FastMCP

from droneblog_mcp.utils.fs import hexo_build, hexo_deploy
from droneblog_mcp.utils.log import log


def register_build_tools(mcp: FastMCP) -> None:
    """注册构建和部署相关 Tools"""

    @mcp.tool()
    async def build(
        clean: bool = True,
    ) -> dict:
        """执行 hexo（可选 clean）generate 构建站点，回传真实构建输出。

        Args:
            clean: 是否先执行 hexo clean，默认 True

        Returns:
            构建结果，``message`` 为 hexo 的真实输出（失败时为错误尾部）
        """
        build_ok, build_msg = hexo_build(clean=clean)
        if build_ok:
            log("OK", "execute", "站点构建成功")
            return {"status": "success", "message": build_msg}
        else:
            log("FAIL", "execute", f"站点构建失败: {build_msg}")
            return {"status": "fail", "message": build_msg}

    @mcp.tool()
    async def deploy(
        build_first: bool = True,
    ) -> dict:
        """执行 hexo deploy 部署到 GitHub Pages，回传真实输出。

        Args:
            build_first: 是否先构建再部署，默认 True

        Returns:
            部署结果
        """
        if build_first:
            build_ok, build_msg = hexo_build(clean=True)
            if not build_ok:
                return {"status": "fail", "message": f"Build failed before deploy:\n{build_msg}"}

        deploy_ok, deploy_msg = hexo_deploy()
        if deploy_ok:
            log("OK", "execute", "站点部署成功")
            return {"status": "success", "message": deploy_msg}
        else:
            log("FAIL", "execute", f"站点部署失败: {deploy_msg}")
            return {"status": "fail", "message": deploy_msg}
