"""DroneBlog MCP Server - Tools Package"""

from mcp.server.fastmcp import FastMCP

from droneblog_mcp.tools.blog import register_blog_tools
from droneblog_mcp.tools.build import register_build_tools
from droneblog_mcp.tools.config import register_config_tools
from droneblog_mcp.tools.pipeline import register_pipeline_tools
from droneblog_mcp.tools.setup import register_setup_tools


def register_all_tools(mcp: FastMCP) -> None:
    """注册所有 Tools"""
    register_setup_tools(mcp)
    register_blog_tools(mcp)
    register_config_tools(mcp)
    register_build_tools(mcp)
    register_pipeline_tools(mcp)


__all__ = ["register_all_tools"]
