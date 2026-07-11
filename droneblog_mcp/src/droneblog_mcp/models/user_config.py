"""DroneBlog MCP Server - User GitHub Configuration"""

import os
import stat
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def mask_secret(value: str) -> str:
    """将密钥脱敏为 ``前缀****末4位``，用于日志/工具返回值，绝不回显完整明文。"""
    if not value:
        return ""
    if len(value) <= 8:
        return "****"
    return f"{value[:4]}****{value[-4:]}"


class UserConfig(BaseSettings):
    """用户 GitHub 配置"""

    model_config = SettingsConfigDict(
        env_prefix="DRONEBLOG_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # GitHub 认证
    github_token: str = Field(
        default="",
        description="GitHub Personal Access Token (需要 repo 权限)",
    )
    github_username: str = Field(
        default="",
        description="GitHub 用户名",
    )

    # 仓库配置
    pages_repo: str = Field(
        default="{username}.github.io",
        description="GitHub Pages 仓库名",
    )
    source_repo: str = Field(
        default="my-blog-source",
        description="Hexo 源码仓库名（同步归档模式）",
    )

    # 工作模式
    sync_mode: str = Field(
        default="local",
        description="工作模式: local(本地) / sync(同步归档)",
    )

    # 部署配置
    deploy_branch: str = Field(
        default="master",
        description="部署分支",
    )
    auto_deploy: bool = Field(
        default=False,
        description="是否自动部署",
    )

    # 本地工作目录
    dir: Path = Field(
        default=Path("."),
        description="博客工作目录",
    )

    @field_validator("sync_mode")
    @classmethod
    def validate_sync_mode(cls, v: str) -> str:
        """验证工作模式"""
        if v not in ("local", "sync"):
            raise ValueError("sync_mode 必须是 'local' 或 'sync'")
        return v

    @property
    def pages_repo_name(self) -> str:
        """Pages 仓库名（已替换 {username}）"""
        return self.pages_repo.format(username=self.github_username)

    @property
    def pages_repo_full(self) -> str:
        """Pages 仓库完整名（owner/repo）"""
        return f"{self.github_username}/{self.pages_repo_name}"

    @property
    def source_repo_full(self) -> str:
        """源码仓库完整名（owner/repo）"""
        return f"{self.github_username}/{self.source_repo}"

    @property
    def is_configured(self) -> bool:
        """是否已配置 GitHub"""
        return bool(self.github_token and self.github_username)

    @property
    def posts_dir(self) -> Path:
        """文章存储目录"""
        return self.dir / "source" / "_posts"

    @property
    def config_file(self) -> Path:
        """站点配置文件"""
        return self.dir / "_config.yml"

    def safe_dump(self) -> dict:
        """导出可对外展示的配置字典：github_token 等敏感字段已脱敏。"""
        data = self.model_dump()
        if data.get("github_token"):
            data["github_token"] = mask_secret(data["github_token"])
        return data


# 全局用户配置实例
_user_config: UserConfig | None = None


def get_user_config() -> UserConfig:
    """获取全局用户配置（懒加载）"""
    global _user_config
    if _user_config is None:
        # 尝试从配置文件加载
        config_path = Path.home() / ".config" / "droneblog" / "config.json"
        if config_path.exists():
            import json
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            _user_config = UserConfig(**data)
        else:
            _user_config = UserConfig()
    return _user_config


def set_user_config(config: UserConfig) -> None:
    """设置全局用户配置"""
    global _user_config
    _user_config = config


def save_user_config(config: UserConfig) -> None:
    """保存用户配置到 ``~/.config/droneblog/config.json``，并收紧权限为 0600。

    注意：文件仍以明文保存 token（否则无法用于鉴权）。建议优先使用
    ``DRONEBLOG_GITHUB_TOKEN`` 环境变量而非持久化 token；本函数仅把权限收紧到
    当前用户可读写，作为最低限度的 at-rest 保护。
    """
    config_dir = Path.home() / ".config" / "droneblog"
    config_dir.mkdir(parents=True, exist_ok=True)

    config_path = config_dir / "config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        import json
        json.dump(config.model_dump(), f, indent=2, ensure_ascii=False, default=str)

    # 仅当前用户可读写；Windows 上 chmod 语义有限，失败时忽略并继续。
    try:
        os.chmod(config_path, stat.S_IRUSR | stat.S_IWUSR)
        os.chmod(config_dir, stat.S_IRWXU)
    except OSError:
        pass
