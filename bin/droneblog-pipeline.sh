#!/bin/bash
# droneblog-pipeline.sh — 已迁移至 bin/droneblog
# 保留此文件仅用于兼容旧别名/工作流。它不再直接调用 OpenAI API 或 nano，
# 而是把参数透传给新的 MCP CLI wrapper（bin/droneblog）。
#
# 新入口：
#   bin/droneblog generate <topic> [category] [tags]
#   bin/droneblog build
#   bin/droneblog deploy
#   bin/droneblog list
#   bin/droneblog read <slug>
#   bin/droneblog status

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/droneblog" "$@"
