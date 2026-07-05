"""DroneBlog MCP Server - Blog Tools"""

from typing import Optional

from mcp.server.fastmcp import FastMCP

from droneblog_mcp.core.pipeline import run_pipeline
from droneblog_mcp.models.config import get_config
from droneblog_mcp.utils.fs import delete_post, list_posts, read_post, write_post
from droneblog_mcp.utils.log import log
from droneblog_mcp.utils.fs import build_frontmatter, parse_frontmatter


def register_blog_tools(mcp: FastMCP) -> None:
    """注册博客相关 Tools"""

    @mcp.tool()
    async def blog_generate(
        topic: str,
        category: str,
        tags: list[str],
        prompt: str = "",
        auto_confirm: bool = False,
        model: str = "",
    ) -> dict:
        """生成一篇技术博客文章，经过完整的 6 阶段流水线

        Args:
            topic: 文章主题，如 "C++20 协程深度解析"
            category: 分类，必须是以下之一: 后端开发、前端技术、系统编程、云原生、人工智能、分布式系统
            tags: 标签列表，2-3 个，如 ["C++", "协程", "异步编程"]
            prompt: 额外提示词，指导 AI 生成特定内容
            auto_confirm: 是否跳过人工审核（默认 false，建议保持 false）
            model: 使用的 AI 模型（默认 gpt-4o-mini）

        Returns:
            包含生成结果的字典，包括文件路径、构建状态、流水线各阶段结果
        """
        config = get_config()
        model = model or config.model

        # 验证分类
        if category not in config.valid_categories:
            return {
                "status": "fail",
                "message": f"Invalid category '{category}'. Must be one of: {config.valid_categories}",
            }

        # 验证标签数量
        if len(tags) < config.min_tags or len(tags) > config.max_tags:
            return {
                "status": "fail",
                "message": f"Tags count {len(tags)} must be between {config.min_tags} and {config.max_tags}",
            }

        try:
            result = run_pipeline(
                topic=topic,
                category=category,
                tags=tags,
                prompt=prompt,
                model=model,
                auto_confirm=auto_confirm,
            )
            return result
        except Exception as e:
            return {
                "status": "fail",
                "message": str(e),
            }

    @mcp.tool()
    async def blog_list(
        category: Optional[str] = None,
        tag: Optional[str] = None,
        year: Optional[int] = None,
        limit: int = 20,
    ) -> list[dict]:
        """列出博客文章，支持多种筛选条件

        Args:
            category: 按分类筛选，如 "后端开发"
            tag: 按标签筛选，如 "C++"
            year: 按年份筛选，如 2025
            limit: 返回数量限制，默认 20

        Returns:
            文章列表，每项包含 slug、title、date、tags、categories、word_count
        """
        return list_posts(category=category, tag=tag, year=year, limit=limit)

    @mcp.tool()
    async def blog_read(
        slug: str,
        include_raw: bool = False,
    ) -> dict:
        """读取单篇博客文章的完整内容

        Args:
            slug: 文章 slug（文件名，不含 .md 后缀）
            include_raw: 是否包含原始 Markdown（含 Front-matter）

        Returns:
            文章详情，包含 title、date、tags、categories、content 等
        """
        post = read_post(slug)
        if not post:
            return {"status": "fail", "message": f"Post not found: {slug}"}

        if not include_raw:
            post.pop("raw_content", None)

        return {"status": "success", "post": post}

    @mcp.tool()
    async def blog_edit(
        slug: str,
        content: Optional[str] = None,
        title: Optional[str] = None,
        tags: Optional[list[str]] = None,
        category: Optional[str] = None,
    ) -> dict:
        """编辑现有博客文章，支持部分更新

        Args:
            slug: 文章 slug（文件名）
            content: 新正文内容（完整替换），为 None 则保持原内容
            title: 新标题，为 None 则保持原标题
            tags: 新标签列表，为 None 则保持原标签
            category: 新分类，为 None 则保持原分类

        Returns:
            编辑结果，包含更新后的文件路径
        """
        post = read_post(slug)
        if not post:
            return {"status": "fail", "message": f"Post not found: {slug}"}

        raw_content = post.get("raw_content", "")
        metadata, body = parse_frontmatter(raw_content)

        # 更新字段
        if title:
            metadata["title"] = title
        if tags is not None:
            metadata["tags"] = tags
        if category:
            metadata["categories"] = [category]
        if content:
            body = content

        # 更新日期
        from datetime import datetime
        metadata["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        new_content = build_frontmatter(metadata, body)
        file_path = write_post(slug, new_content)

        log("OK", "execute", f"文章已编辑: {slug}")

        return {
            "status": "success",
            "message": f"Post updated: {slug}",
            "file": str(file_path),
        }

    @mcp.tool()
    async def blog_delete(
        slug: str,
        confirm: bool = False,
    ) -> dict:
        """删除博客文章（需要确认）

        Args:
            slug: 文章 slug（文件名）
            confirm: 确认删除，必须为 True 才会执行

        Returns:
            删除结果
        """
        if not confirm:
            return {
                "status": "fail",
                "message": "Deletion not confirmed. Set confirm=True to delete.",
            }

        if delete_post(slug):
            log("OK", "execute", f"文章已删除: {slug}")
            return {"status": "success", "message": f"Post deleted: {slug}"}
        else:
            return {"status": "fail", "message": f"Post not found: {slug}"}
