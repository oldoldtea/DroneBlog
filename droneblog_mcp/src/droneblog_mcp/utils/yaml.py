"""DroneBlog MCP Server - YAML Utilities"""

from pathlib import Path
from typing import Any

import yaml

from droneblog_mcp.models.config import get_config


def load_yaml(path: Path) -> dict | None:
    """加载 YAML 文件"""
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return None


def save_yaml(path: Path, data: dict) -> bool:
    """保存 YAML 文件"""
    try:
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        return True
    except Exception:
        return False


def get_nested_value(data: dict, key_path: str) -> Any:
    """通过点号路径获取嵌套值"""
    keys = key_path.split(".")
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    return current


def set_nested_value(data: dict, key_path: str, value: Any) -> dict:
    """通过点号路径设置嵌套值。

    中间节点不存在时自动创建为 dict；若已存在但**不是** dict（如对已有标量
    再深入一层），抛 ``ValueError``——由 ``set_site_config`` 转为友好的失败
    结果，而不是让 ``TypeError`` 逃逸成工具崩溃。
    """
    keys = key_path.split(".")
    current = data
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        elif not isinstance(current[key], dict):
            raise ValueError(
                f"配置路径 '{key_path}' 的中间节点 '{key}' 不是映射"
                f"（当前值类型 {type(current[key]).__name__}），无法继续深入"
            )
        current = current[key]
    current[keys[-1]] = value
    return data


def get_site_config(scope: str = "site") -> dict | None:
    """获取站点或主题配置"""
    config = get_config()
    if scope == "site":
        return load_yaml(config.config_file)
    elif scope == "theme":
        return load_yaml(config.theme_config_file)
    elif scope == "all":
        return {
            "site": load_yaml(config.config_file) or {},
            "theme": load_yaml(config.theme_config_file) or {},
        }
    return None


def set_site_config(scope: str, key_path: str, value: Any) -> tuple[bool, str]:
    """修改站点或主题配置"""

    config = get_config()
    if scope == "site":
        path = config.config_file
    elif scope == "theme":
        path = config.theme_config_file
    else:
        return False, f"Unknown scope: {scope}"

    data = load_yaml(path)
    if data is None:
        return False, f"Failed to load config: {path}"

    try:
        set_nested_value(data, key_path, value)
    except ValueError as e:
        return False, str(e)

    if save_yaml(path, data):
        return True, f"Config updated: {scope}.{key_path} = {value}"
    return False, "Failed to save config"
