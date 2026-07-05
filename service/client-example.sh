#!/bin/bash
# client-example.sh — DroneBlog Pipeline Service 客户端示例
#
# 用法:
#   ./client-example.sh "文章标题" "分类" "标签"

set -e

SERVICE_URL="${DRONEBLOG_URL:-http://127.0.0.1:8765}"
TOPIC="${1:-}"
CATEGORY="${2:-后端开发}"
TAGS="${3:-}"

if [ -z "$TOPIC" ]; then
  echo "用法: $0 <文章标题> [分类] [标签]"
  echo "示例: $0 'C++20 协程入门' '后端开发' 'C++,协程'"
  exit 1
fi

echo "========================================"
echo "DroneBlog Pipeline Client"
echo "========================================"
echo "Service: $SERVICE_URL"
echo "Topic:   $TOPIC"
echo "Category: $CATEGORY"
echo "Tags:    ${TAGS:-<默认>}"
echo ""

# 检查服务是否可用
if ! curl -s "$SERVICE_URL/health" > /dev/null 2>&1; then
  echo "❌ 服务未启动"
  echo "   请先运行: ./service/droneblogctl.sh start"
  exit 1
fi

echo "✓ 服务可用"
echo ""

# 发送生成请求
echo "发送请求..."
RESPONSE=$(curl -s -X POST "$SERVICE_URL/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d "{
    \"topic\": \"$TOPIC\",
    \"category\": \"$CATEGORY\",
    \"tags\": \"$TAGS\"
  }")

# 解析响应
if echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(0 if d.get('status')=='success' else 1)" 2>/dev/null; then
  echo ""
  echo "✅ 生成成功!"
  echo ""
  echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
else
  echo ""
  echo "❌ 生成失败"
  echo ""
  echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
  exit 1
fi
