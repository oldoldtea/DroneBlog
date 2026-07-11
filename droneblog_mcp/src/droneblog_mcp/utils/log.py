"""DroneBlog MCP Server - Logging Utilities"""

from datetime import datetime, timedelta, timezone

from droneblog_mcp.models.config import get_config


def log(status: str, stage: str, message: str) -> str:
    """写入流水线日志"""
    config = get_config()
    log_file = config.log_file

    tz = timezone(timedelta(hours=8))
    ts = datetime.now(tz).strftime("%Y-%m-%dT%H:%M:%S+08:00")
    line = f"[{ts}] [{status}] [{stage}] {message}\n"

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line)

    return line.strip()


def read_log_lines(limit: int = 100) -> list[str]:
    """读取最近的日志行"""
    config = get_config()
    log_file = config.log_file

    if not log_file.exists():
        return []

    try:
        with open(log_file, encoding="utf-8") as f:
            lines = f.readlines()
        return [line.strip() for line in lines[-limit:]]
    except Exception:
        return []


def parse_log_status() -> dict:
    """解析日志中的流水线状态"""
    lines = read_log_lines(200)
    stages = {}

    for line in lines:
        # 格式: [timestamp] [status] [stage] message
        import re

        match = re.match(r"\[.*?\] \[(\w+)\] \[(\w+)\] (.*)", line)
        if match:
            status, stage, message = match.groups()
            stages[stage] = {"status": status, "message": message}

    return stages
