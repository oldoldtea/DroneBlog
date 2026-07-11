"""DroneBlog MCP Server - Main Server"""

from mcp.server.fastmcp import FastMCP

from droneblog_mcp.models.config import get_config
from droneblog_mcp.tools import register_all_tools
from droneblog_mcp.utils.fs import list_posts, read_post
from droneblog_mcp.utils.log import read_log_lines
from droneblog_mcp.utils.yaml import get_site_config


def create_server() -> FastMCP:
    """创建并配置 MCP Server"""
    # 触发一次配置加载：DRONEBLOG_DIR 非法时尽早失败，而不是等到首个工具调用。
    get_config()

    mcp = FastMCP("droneblog")

    # 注册所有 Tools
    register_all_tools(mcp)

    # 注册 Resources
    @mcp.resource("blog://{slug}")
    async def get_blog_post(slug: str) -> str:
        """获取单篇博客文章的 Markdown 内容"""
        post = read_post(slug)
        if not post:
            return f"# Error\n\nPost not found: {slug}"
        return post.get("raw_content", post.get("content", ""))

    @mcp.resource("config://site")
    async def get_site_config_resource() -> str:
        """获取站点配置"""
        cfg = get_site_config("site")
        if not cfg:
            return "# Error\n\nFailed to load site config"
        import yaml

        return yaml.dump(cfg, allow_unicode=True, sort_keys=False)

    @mcp.resource("config://theme")
    async def get_theme_config_resource() -> str:
        """获取主题配置"""
        cfg = get_site_config("theme")
        if not cfg:
            return "# Error\n\nFailed to load theme config"
        import yaml

        return yaml.dump(cfg, allow_unicode=True, sort_keys=False)

    @mcp.resource("pipeline://log")
    async def get_pipeline_log() -> str:
        """获取流水线日志"""
        lines = read_log_lines(100)
        if not lines:
            return "# Pipeline Log\n\nNo log entries found."
        return "# Pipeline Log\n\n" + "\n".join(lines)

    @mcp.resource("blogs://list")
    async def get_blog_list() -> str:
        """获取博客文章列表（collection，区别于单篇的 ``blog://{slug}``，避免路由冲突）"""
        posts = list_posts(limit=50)
        if not posts:
            return "# Blog Posts\n\nNo posts found."

        lines = ["# Blog Posts\n"]
        for post in posts:
            lines.append(f"## {post['title']}")
            lines.append(f"- **Slug**: {post['slug']}")
            lines.append(f"- **Date**: {post['date']}")
            lines.append(f"- **Categories**: {', '.join(post['categories'])}")
            lines.append(f"- **Tags**: {', '.join(post['tags'])}")
            lines.append(f"- **Words**: {post['word_count']}")
            lines.append("")

        return "\n".join(lines)

    # 注册 Prompts
    @mcp.prompt()
    async def blog_writing() -> str:
        """博客写作助手提示词"""
        return """你是一个专业的技术博客写作助手。请帮助用户：

1. 确定文章主题和技术方向
2. 规划文章结构（引言、核心内容、总结）
3. 提供代码示例和最佳实践
4. 确保文章符合 DroneBlog 的内容规范：
   - 标题格式: '{技术名} {内容类型}'
   - 使用 YAML Front-matter: title, date, tags, categories
   - tags: 2-3 个（核心技术 → 主题方向 → 细分领域）
   - categories: 后端开发 / 前端技术 / 系统编程 / 云原生 / 人工智能 / 分布式系统
   - 内容结构: 引言 → 分章节正文（含代码示例） → 总结
   - 语言: 简体中文
   - 代码块使用 ```cpp 等语言标识

你可以使用以下工具：
- blog_generate: 生成新文章
- blog_list: 列出已有文章
- blog_read: 读取文章内容
- blog_edit: 编辑文章
- build: 构建站点
- deploy: 部署站点
"""

    @mcp.prompt()
    async def tech_analysis() -> str:
        """技术文章分析提示词"""
        return """你是一个技术文档分析专家。请帮助用户：

1. 分析现有技术文章的质量
2. 提出改进建议
3. 检查技术准确性
4. 优化文章结构和可读性

分析维度：
- 内容完整性：是否覆盖了核心概念
- 代码质量：示例是否正确、可运行
- 结构清晰度：章节划分是否合理
- 语言表达：是否简洁明了
- 技术准确性：概念和术语是否正确

你可以使用 blog_read 工具读取文章内容进行分析。
"""

    @mcp.prompt()
    async def blog_idea_generator() -> str:
        """博客选题生成提示词"""
        return """你是一个技术博客选题专家。请帮助用户生成有价值的博客选题。

请根据用户的技术领域和兴趣方向，提供：
1. 5-10 个具体的博客选题
2. 每个选题的简要说明
3. 建议的分类和标签
4. 目标读者群体

选题原则：
- 有实际价值，能解决读者问题
- 有技术深度，不是简单的入门教程
- 结合最新技术趋势
- 有代码示例和实践指导

当前博客分类体系：
- 后端开发
- 前端技术
- 系统编程
- 云原生
- 人工智能
- 分布式系统
"""

    return mcp
