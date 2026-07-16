#!/bin/bash
# generate-and-archive.sh — 已弃用（deprecated）
#
# 旧逻辑：直接调用 OpenAI API + nano + GitHub repository dispatch。
# 新路径：归档/同步已收敛到 MCP Server 的 setup_sync_posts 或 GitHub Actions。
#
# 推荐用法：
#   bin/droneblog generate "文章主题" "分类" "标签1,标签2"
#   # 审核后提交到源码仓库，由 GitHub Actions 自动部署。

set -e

echo "[WARN] generate-and-archive.sh 已弃用。" >&2
echo "       请使用 bin/droneblog 或 MCP 客户端生成内容。" >&2
echo "       GitHub 同步请使用 MCP setup_sync_posts 或 GitHub Actions。" >&2
exit 1
