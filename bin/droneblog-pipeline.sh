#!/bin/bash
# droneblog-pipeline.sh — 跨项目触发 DroneBlog AI 流水线
#
# 用法:
#   在其他项目目录下执行:
#   export OPENAI_API_KEY=sk-xxx
#   /path/to/droneblog/bin/droneblog-pipeline.sh "文章主题" "分类" "标签"
#
# 流程:
#   1. 需求分析 — 解析参数，确定任务类型=content_creation
#   2. Skill 识别 — 无需外部 Skill，使用通用能力
#   3. AI 生成 — 调用 OpenAI API 生成符合规范的 Markdown
#   4. 人工审核 — 打开编辑器让用户修改
#   5. 流水线校验 — Front-matter、文件名、标签数量
#   6. 本地写入 — 写入 DroneBlog 的 source/_posts/
#   7. 构建验证 — hexo clean && hexo generate
#   8. 输出规范 — 显示结果摘要

set -e

# ── 配置 ──
DRONEBLOG_DIR="$(cd "$(dirname "$0")/.." && pwd)"
POSTS_DIR="$DRONEBLOG_DIR/source/_posts"
LOG_FILE="$DRONEBLOG_DIR/.ai-pipeline.log"

# ── 参数 ──
TOPIC="${1:-}"
CATEGORY="${2:-后端开发}"
TAGS="${3:-}"
EXTRA_PROMPT="${4:-}"

if [ -z "$TOPIC" ]; then
  echo "用法: $0 <文章主题> [分类] [标签] [额外提示]"
  echo "示例: $0 'C++20 协程' '后端开发' 'C++,协程' '重点讲co_await'"
  exit 1
fi

if [ -z "$OPENAI_API_KEY" ]; then
  echo "[Pipeline] ❌ ERROR: 请设置 OPENAI_API_KEY 环境变量"
  exit 1
fi

# ── 工具函数 ──
log() {
  local status="$1"
  local stage="$2"
  local msg="$3"
  local ts
  ts=$(date +"%Y-%m-%dT%H:%M:%S+08:00")
  echo "[$ts] [$status] [$stage] $msg" | tee -a "$LOG_FILE"
}

# ── 阶段 1: 需求分析 ──
echo ""
echo "[Pipeline] 阶段 1/6: 需求分析"
echo "  任务类型: content_creation"
echo "  技术关键词: $TOPIC"
echo "  分类: $CATEGORY"
echo "  标签: ${TAGS:-$CATEGORY}"
log "OK" "analysis" "任务类型=content_creation, 关键词=$TOPIC"

# ── 阶段 2: Skill 识别 ──
echo ""
echo "[Pipeline] 阶段 2/6: Skill 识别"
echo "  本地注册表: 无匹配 Skill"
echo "  使用通用能力执行"
log "OK" "skill_match" "无匹配 Skill，使用通用能力"

# ── 阶段 3: 执行 — AI 生成 ──
echo ""
echo "[Pipeline] 阶段 3/6: 执行流程 — AI 生成文章"

# 生成 slug
SLUG=$(echo "$TOPIC" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//;s/-$//')
DATE=$(date +"%Y-%m-%d %H:%M:%S")
TMP_FILE="/tmp/${SLUG}.md"

echo "  生成 slug: $SLUG"
echo "  日期: $DATE"

# 调用 AI
SYSTEM_PROMPT="你是一个资深技术博客作者，为 DroneBlog 写作。

文章规范（必须严格遵守）：
1. 标题格式: '{技术名} {内容类型}'，如 'C++ 核心特性深度解析'
2. 使用 YAML Front-matter: title, date, tags, categories
3. tags: 2-3 个，第1个是核心技术/语言，第2个是主题方向
4. categories: 单一分类，只能是以下之一:
   后端开发 / 前端技术 / 系统编程 / 云原生 / 人工智能 / 分布式系统
5. 内容结构: 引言 → 分章节正文（含代码示例） → 总结
6. 语言: 简体中文
7. 代码块使用 ```cpp 等语言标识"

USER_PROMPT="请写一篇技术博客。

主题: $TOPIC
分类: $CATEGORY
${TAGS:+$'\n标签要求: '$TAGS}
${EXTRA_PROMPT:+$'\n额外要求: '$EXTRA_PROMPT}

请输出完整的 Markdown 文件内容，包含 YAML Front-matter。"

echo "  正在调用 AI 生成..."
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

CONTENT=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'])")

if [ -z "$CONTENT" ] || [ "$CONTENT" = "None" ]; then
  log "FAIL" "execute" "AI 生成失败"
  exit 1
fi

# 提取 AI 生成的 Front-matter 中的 title
AI_TITLE=$(echo "$CONTENT" | grep "^title:" | head -1 | sed 's/title: //' | sed 's/^["'\''']*//;s/["'\''']*$//')
TITLE="${AI_TITLE:-$TOPIC}"

# 写入临时文件
echo "$CONTENT" > "$TMP_FILE"

echo "  AI 生成完成: $TITLE"
log "OK" "execute" "AI 生成完成: $TITLE"

# ── 阶段 4: 人工审核 ──
echo ""
echo "[Pipeline] 阶段 4/6: 人工审核"
echo "  正在打开编辑器..."
${EDITOR:-nano} "$TMP_FILE"

# 重新读取（用户可能修改了 title）
USER_TITLE=$(grep "^title:" "$TMP_FILE" | head -1 | sed 's/title: //' | sed 's/^["'\''']*//;s/["'\''']*$//')
TITLE="${USER_TITLE:-$TITLE}"

read -p "[Pipeline] 确认提交? (y/N): " CONFIRM
if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
  log "ABORT" "execute" "用户取消提交"
  echo "[Pipeline] 已取消"
  rm -f "$TMP_FILE"
  exit 0
fi

log "OK" "execute" "人工审核通过"

# ── 阶段 5: 流程合规审核 — 校验规范 ──
echo ""
echo "[Pipeline] 阶段 5/6: 流程合规审核"

ERRORS=0

# 5.1 Front-matter 校验
HEAD_LINE=$(head -n 1 "$TMP_FILE")
if [ "$HEAD_LINE" != "---" ]; then
  echo "  ❌ Front-matter: 缺少 --- 开头"
  ERRORS=$((ERRORS + 1))
else
  echo "  ✓ Front-matter: 格式正确"
fi

if ! grep -qE '^title:\s*.+' "$TMP_FILE"; then
  echo "  ❌ Front-matter: 缺少 title"
  ERRORS=$((ERRORS + 1))
else
  echo "  ✓ Front-matter: title 存在"
fi

if ! grep -qE '^date:' "$TMP_FILE"; then
  echo "  ⚠ Front-matter: 缺少 date，自动添加"
  # 在 --- 后面插入 date
  sed -i "0,/^---$/{s/^---$/---\ndate: $DATE/}" "$TMP_FILE"
fi

# 5.2 标签数量校验
TAG_COUNT=$(grep "^  - " "$TMP_FILE" | wc -l)
if [ "$TAG_COUNT" -lt 2 ] || [ "$TAG_COUNT" -gt 3 ]; then
  echo "  ⚠ 标签数量: $TAG_COUNT 个（建议 2-3 个）"
else
  echo "  ✓ 标签数量: $TAG_COUNT 个"
fi

# 5.3 文件名校验
if echo "$SLUG" | grep -qE '[A-Z_]'; then
  echo "  ❌ 文件名: 包含大写或下划线"
  ERRORS=$((ERRORS + 1))
else
  echo "  ✓ 文件名: $SLUG.md（符合 kebab-case）"
fi

if [ "$ERRORS" -gt 0 ]; then
  log "FAIL" "compliance_audit" "发现 $ERRORS 个错误，请修复后重试"
  exit 1
fi

log "OK" "compliance_audit" "全部合规"

# ── 阶段 6: 安全审查 ──
echo ""
echo "[Pipeline] 阶段 6/6: 安全审查"

# 敏感信息扫描
if grep -iE '(api[_-]?key|token|password|secret)[[:space:]]*[:=]' "$TMP_FILE"; then
  echo "  ⚠ 检测到可能的敏感信息模式，请确认"
  read -p "  是否继续? (y/N): " SEC_CONFIRM
  if [ "$SEC_CONFIRM" != "y" ]; then
    log "ABORT" "security" "用户取消（敏感信息警告）"
    exit 0
  fi
else
  echo "  ✓ 敏感信息扫描: 通过"
fi

log "OK" "security" "安全审查通过"

# ── 写入目标位置 ──
echo ""
echo "[Pipeline] 写入文件..."
mkdir -p "$POSTS_DIR"
cp "$TMP_FILE" "$POSTS_DIR/${SLUG}.md"
echo "  ✓ 写入: source/_posts/${SLUG}.md"

# ── 构建验证 ──
echo ""
echo "[Pipeline] 构建验证: hexo clean && hexo generate"
cd "$DRONEBLOG_DIR"
if npx hexo clean >/dev/null 2>&1 && npx hexo generate 2>&1 | tail -3; then
  log "OK" "execute" "构建验证通过"
  BUILD_OK=1
else
  log "FAIL" "execute" "构建验证失败"
  BUILD_OK=0
fi

# ── 输出规范 ──
echo ""
echo "========================================"
echo "[Pipeline] 任务完成"
echo "========================================"
echo ""
echo "修改摘要: 新增博客文章"
echo ""
echo "文件清单:"
echo "  | 新增 | source/_posts/${SLUG}.md |"
echo ""
if [ "$BUILD_OK" = 1 ]; then
  echo "验证结果: ✅ 构建通过"
else
  echo "验证结果: ❌ 构建失败，请检查文章格式"
fi
echo ""
echo "Skill 匹配结果: 无匹配，使用通用能力"
echo ""
echo "后续建议:"
echo "  1. 执行 'hexo deploy' 部署到线上"
echo "  2. 或提交到 Git: git add source/_posts/ && git commit -m '[文章] $TITLE'"
echo ""

# 清理
rm -f "$TMP_FILE"

log "OK" "output" "任务完成: $TITLE"
