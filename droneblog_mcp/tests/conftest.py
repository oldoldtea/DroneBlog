"""pytest 共享配置：为测试提供一个存在的 DRONEBLOG_DIR。"""

import os
from pathlib import Path

# DroneBlog 仓库根目录（包含 _config.yml 与 source/_posts），用于 create_server 的配置校验。
REPO_ROOT = Path(__file__).resolve().parents[2]

# 必须在导入 droneblog_mcp 之前设置，因为 create_server 会校验目录存在。
os.environ.setdefault("DRONEBLOG_DIR", str(REPO_ROOT))
