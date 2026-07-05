#!/bin/bash
# generate-and-archive.sh — 本地 AI 生成 + 人工审核 + 自动归档
#
# 用法:
#   export OPENAI_API_KEY=sk-xxx
#   export ARCHIVE_PAT=ghp-xxx
#   ./scripts/generate-and-archive.sh "C++ 协程入门" "后端开发"
#
# 流程:
#   1. 调用 AI API 生成文章
#   2. 打开编辑器供用户审核修改
#   3. 用户确认后发送归档请求到 DroneBlog

set -e

# ── 参数解析 ──
TITLE="${1:-}"
CATEGORY="${2:-后端开发}"
TAGS="${3:-}"
PROMPT="${4:-}"

if [ -z "$TITLE" ]; then
  echo "用法: $0 <文章标题> [分类] [标签] [额外提示]"
  echo "示例: $0 'C++ 协程入门' '后端开发' 'C++,协程' '重点讲co_await'"
  exit 1
fi

# ── 检查环境变量 ──
if [ -z "$OPENAI_API_KEY" ]; then
  echo "ERROR: 请设置 OPENAI_API_KEY 环境变量"
  exit 1
fi

if [ -z "$ARCHIVE_PAT" ]; then
  echo "ERROR: 请设置 ARCHIVE_PAT 环境变量（GitHub Personal Access Token）"
  exit 1
fi

# ── 生成 slug ──
SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//;s/-$//')
DATE=$(date +"%Y-%m-%d %H:%M:%S")
TMP_FILE="/tmp/${SLUG}.md"

echo "========================================"
echo "标题: $TITLE"
echo "Slug: $SLUG"
echo "日期: $DATE"
echo "分类: $CATEGORY"
echo "标签: ${TAGS:-$CATEGORY}"
echo "========================================"
echo ""

# ── 调用 AI 生成文章 ──
echo "[1/4] 正在调用 AI 生成文章..."

SYSTEM_PROMPT="你是一个资深技术博客作者，擅长写深入浅出的技术教程。
要求：
- 使用标准 Markdown 格式
- 内容结构清晰：引言、正文（分章节）、总结
- 包含实用的代码示例
- 语言：简体中文
- 面向有一定基础的开发者"

USER_PROMPT="请写一篇技术博客文章。

标题：${TITLE}
分类：${CATEGORY}
${TAGS:+$'\n标签：'$TAGS}
${PROMPT:+$'\n额外要求：'$PROMPT}

请直接输出文章正文内容（不需要 Front-matter，我会自动添加）。"

# 调用 OpenAI API
RESPONSE=$(curl -s https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"gpt-4o-mini\",
    \"messages\": [
      {\"role\": \"system\", \"content\": \"$SYSTEM_PROMPT\"},
      {\"role\": \"user\", \"content\": \"$USER_PROMPT\"}
    ],
    \"temperature\": 0.7
  }")

# 提取内容
CONTENT=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'])")

if [ -z "$CONTENT" ] || [ "$CONTENT" = "None" ]; then
  echo "ERROR: AI 生成失败"
  echo "API 响应: $RESPONSE"
  exit 1
fi

# ── 组装完整文章（含 Front-matter）──
cat > "$TMP_FILE" << EOF
---
title: ${TITLE}
date: ${DATE}
tags:
$(echo "${TAGS:-$CATEGORY}" | tr ',' '\n' | sed 's/^/  - /')
categories:
  - ${CATEGORY}
---

${CONTENT}
EOF

echo "[2/4] 文章已生成，保存到: $TMP_FILE"
echo ""

# ── 打开编辑器供用户审核 ──
echo "[3/4] 正在打开编辑器供你审核修改..."
echo "（保存并关闭编辑器后继续）"
echo ""

# 使用系统默认编辑器
${EDITOR:-nano} "$TMP_FILE"

# ── 用户确认 ──
echo ""
echo "========================================"
echo "文章预览（前 20 行）:"
echo "========================================"
head -20 "$TMP_FILE"
echo "..."
echo ""

read -p "确认发送归档请求? (y/N): " CONFIRM
if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
  echo "已取消，文章保留在: $TMP_FILE"
  exit 0
fi

# ── Base64 编码 ──
CONTENT_B64=$(base64 -w 0 "$TMP_FILE")

# ── 发送归档请求 ──
echo "[4/4] 正在发送归档请求到 DroneBlog..."

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: token $ARCHIVE_PAT" \
  https://api.github.com/repos/oldoldtea/DroneBlog/dispatches \
  -d "{
    \"event_type\": \"archive-blog\",
    \"client_payload\": {
      \"mode\": \"direct\",
      \"source_repo\": \"local-cli\",
      \"article_title\": \"$TITLE\",
      \"article_slug\": \"$SLUG\",
      \"content_base64\": \"$CONTENT_B64\"
    }
  }")

if [ "$HTTP_CODE" = "204" ]; then
  echo ""
  echo "✅ 归档请求发送成功！"
  echo "   请访问 https://github.com/oldoldtea/DroneBlog/actions 查看执行状态"
  rm -f "$TMP_FILE"
else
  echo ""
  echo "❌ 归档请求失败，HTTP 状态码: $HTTP_CODE"
  echo "   文章保留在: $TMP_FILE"
  exit 1
fi
