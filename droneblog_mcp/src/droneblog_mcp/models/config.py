"""DroneBlog MCP Server - Configuration Models"""

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DroneBlogConfig(BaseSettings):
    """DroneBlog MCP Server 配置"""

    model_config = SettingsConfigDict(
        env_prefix="DRONEBLOG_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 必需配置
    dir: Path = Field(
        default=Path("."),
        description="博客工作目录（包含 _config.yml 的目录）",
    )
    openai_api_key: str = Field(
        default="",
        description="OpenAI API Key",
    )
    openai_base_url: str = Field(
        default="https://api.openai.com/v1",
        description="OpenAI 兼容 API 的根地址（便于走代理或兼容端点）",
    )

    # 可选配置
    model: str = Field(
        default="gpt-4o-mini",
        description="默认使用的 AI 模型",
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="AI 生成温度",
    )
    max_tokens: int = Field(
        default=4000,
        ge=100,
        le=8000,
        description="最大生成 token 数",
    )
    auto_confirm: bool = Field(
        default=False,
        description="是否默认跳过人工审核（仅用于自动化场景）",
    )
    log_level: str = Field(
        default="info",
        description="日志级别",
    )

    # 分类和标签规范（来自 AGENTS.md）
    valid_categories: list[str] = Field(
        default=[
            "后端开发",
            "前端技术",
            "系统编程",
            "云原生",
            "人工智能",
            "分布式系统",
        ],
        description="有效的文章分类列表",
    )
    min_tags: int = Field(default=2, description="最少标签数")
    max_tags: int = Field(default=3, description="最多标签数")

    @field_validator("dir")
    @classmethod
    def validate_dir(cls, v: Path) -> Path:
        """验证工作目录"""
        path = v.resolve()
        if not path.exists():
            raise ValueError(f"工作目录不存在: {path}")
        return path

    @property
    def posts_dir(self) -> Path:
        """文章存储目录"""
        return self.dir / "source" / "_posts"

    @property
    def config_file(self) -> Path:
        """站点配置文件"""
        return self.dir / "_config.yml"

    @property
    def theme_config_file(self) -> Path:
        """主题配置文件"""
        return self.dir / "themes" / "hexo-theme-maple" / "_config.yml"

    @property
    def log_file(self) -> Path:
        """流水线日志文件"""
        return self.dir / ".ai-pipeline.log"

    @property
    def scaffold_dir(self) -> Path:
        """模板目录"""
        return self.dir / "scaffolds"


# 全局配置实例
_config: DroneBlogConfig | None = None


def get_config() -> DroneBlogConfig:
    """获取全局配置（懒加载）"""
    global _config
    if _config is None:
        _config = DroneBlogConfig()
    return _config


def set_config(config: DroneBlogConfig) -> None:
    """设置全局配置"""
    global _config
    _config = config
