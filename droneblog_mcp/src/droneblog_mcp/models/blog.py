"""DroneBlog MCP Server - Blog Data Models"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class BlogPost(BaseModel):
    """博客文章数据模型"""

    slug: str = Field(description="文章 slug（文件名，kebab-case）")
    title: str = Field(description="文章标题")
    date: datetime = Field(description="发布日期")
    updated: Optional[datetime] = Field(default=None, description="更新日期")
    tags: List[str] = Field(default=[], description="标签列表")
    categories: List[str] = Field(default=[], description="分类列表")
    content: str = Field(default="", description="文章正文（Markdown）")
    raw_content: str = Field(default="", description="完整原始内容（含 Front-matter）")
    excerpt: str = Field(default="", description="文章摘要")
    word_count: int = Field(default=0, description="字数统计")

    class Config:
        json_encoders = {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")}


class BlogPostSummary(BaseModel):
    """博客文章摘要（用于列表）"""

    slug: str = Field(description="文章 slug")
    title: str = Field(description="文章标题")
    date: str = Field(description="发布日期")
    tags: List[str] = Field(default=[], description="标签列表")
    categories: List[str] = Field(default=[], description="分类列表")
    word_count: int = Field(default=0, description="字数统计")


class PipelineStage(BaseModel):
    """流水线阶段状态"""

    name: str = Field(description="阶段名称")
    status: str = Field(description="状态: ok / fail / warn / pending")
    message: str = Field(default="", description="状态消息")
    timestamp: Optional[str] = Field(default=None, description="完成时间")


class PipelineStatus(BaseModel):
    """流水线整体状态"""

    ready: bool = Field(default=True, description="流水线是否就绪")
    stages: List[PipelineStage] = Field(default=[], description="各阶段状态")
    current_stage: Optional[str] = Field(default=None, description="当前执行阶段")
    log_path: str = Field(description="日志文件路径")


class GenerationResult(BaseModel):
    """文章生成结果"""

    status: str = Field(description="success / fail")
    message: str = Field(description="结果消息")
    file: str = Field(description="生成的文件路径")
    slug: str = Field(description="文章 slug")
    title: str = Field(description="文章标题")
    build_status: str = Field(description="构建状态: passed / failed")
    pipeline_stages: dict = Field(default={}, description="各阶段执行结果")
