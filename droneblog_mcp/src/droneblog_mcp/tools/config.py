"""DroneBlog MCP Server - Config Tools"""

from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from droneblog_mcp.models.config import get_config
from droneblog_mcp.utils.log import log
from droneblog_mcp.utils.yaml import get_site_config, set_site_config


def register_config_tools(mcp: FastMCP) -> None:
    """注册配置相关 Tools"""

    @mcp.tool()
    async def config_get(
        scope: str = "site",
    ) -> dict:
        """获取站点或主题配置

        Args:
            scope: 配置范围，可选值: site（站点配置）、theme（主题配置）、all（全部）

        Returns:
            配置内容字典
        """
        config = get_site_config(scope)
        if config is None:
            return {"status": "fail", "message": f"Failed to load config: {scope}"}

        return {"status": "success", "scope": scope, "config": config}

    @mcp.tool()
    async def config_set(
        scope: str,
        key: str,
        value: Any,
    ) -> dict:
        """修改站点或主题配置

        Args:
            scope: 配置范围，可选值: site（站点配置）、theme（主题配置）
            key: 配置键，支持点号路径，如 "url"、"deploy.branch"
            value: 配置值，可以是字符串、数字、布尔值、列表等

        Returns:
            修改结果
        """
        ok, msg = set_site_config(scope, key, value)
        if ok:
            log("OK", "execute", f"配置已更新: {scope}.{key}")
            return {"status": "success", "message": msg}
        else:
            return {"status": "fail", "message": msg}
