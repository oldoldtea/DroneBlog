"""打包完整性测试：包可导入、Server 可实例化、工具已注册。

历史上因打包布局缺失模块（tools/setup 等），`import droneblog_mcp` 即
ModuleNotFoundError。本测试守住这条底线。
"""

import asyncio

import pytest


def test_import_package():
    import droneblog_mcp  # noqa: F401

    assert droneblog_mcp.__version__


def test_create_server_does_not_raise():
    from droneblog_mcp.server import create_server

    mcp = create_server()
    assert mcp is not None


def test_all_tools_registered():
    """通过 FastMCP 的 list_tools（若可用）校验工具数量与关键工具。"""
    from droneblog_mcp.server import create_server

    mcp = create_server()
    if not hasattr(mcp, "list_tools"):
        pytest.skip("当前 mcp 版本未暴露 list_tools，由 stdio 握手测试覆盖")

    tools = asyncio.run(mcp.list_tools())
    names = {t.name for t in tools}

    expected = {
        "setup_init",
        "setup_status",
        "setup_sync_posts",
        "setup_update_config",
        "blog_generate",
        "blog_list",
        "blog_read",
        "blog_edit",
        "blog_delete",
        "config_get",
        "config_set",
        "build",
        "deploy",
        "pipeline_status",
        "pipeline_run",
    }
    missing = expected - names
    assert not missing, f"缺少工具: {missing}"
    assert len(names) >= len(expected)
