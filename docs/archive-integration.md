# 跨工程归档集成指南

> 本文档面向需要在其他工程中触发 DroneBlog 归档行为的开发者。

## 架构概览

```
┌─────────────────┐     repository_dispatch      ┌─────────────────┐
│   源工程 (A)    │  ─────────────────────────►  │   DroneBlog     │
│                 │    Payload: 文章元数据       │  (本仓库)       │
│  1. 生成文章     │         + Base64 内容        │                 │
│  2. 触发归档     │                            │  1. 解析 Payload │
│  3. 写本地日志   │                            │  2. 写 .ai-pipeline.log
│                 │                            │  3. 写入文章     │
│                 │                            │  4. hexo generate
│                 │                            │  5. git commit & push
└─────────────────┘                            └─────────────────┘
```

## 触发方式

使用 GitHub `repository_dispatch` API 发送归档请求。

### 前提条件

1. **DroneBlog 仓库需配置 Personal Access Token (PAT)**
   - 在 DroneBlog 仓库 Settings → Secrets and variables → Actions 中添加 `ARCHIVE_PAT`
   - Token 需要 `repo` 权限

2. **源工程需知道 DroneBlog 的仓库地址**

### API 调用示例

```bash
# 在源工程的 CI / GitHub Actions 中执行
curl -X POST \
  -H "Authorization: token ${{ secrets.ARCHIVE_PAT }}" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/oldoldtea/oldoldtea.github.io/dispatches \
  -d '{
    "event_type": "archive-blog",
    "client_payload": {
      "source_repo": "oldoldtea/project-a",
      "source_branch": "main",
      "commit_sha": "abc123",
      "article_title": "C++ 并发编程实战",
      "article_slug": "cpp-concurrency-practice",
      "article_date": "2026-05-20 10:00:00",
      "article_tags": "C++,并发编程",
      "article_categories": "后端开发",
      "content_base64": "LS0tCnRpdGxlOiBD..."
    }
  }'
```

### Payload 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `source_repo` | ✅ | 源工程仓库名，如 `oldoldtea/project-a` |
| `source_branch` | ✅ | 源分支名 |
| `commit_sha` | ✅ | 触发归档的 commit SHA |
| `article_title` | ✅ | 文章标题 |
| `article_slug` | ✅ | 文章文件名（不含 .md） |
| `article_date` | ✅ | 发布日期 `YYYY-MM-DD HH:mm:ss` |
| `article_tags` | ✅ | 标签，逗号分隔 |
| `article_categories` | ✅ | 分类，逗号分隔 |
| `content_base64` | ✅ | 完整 Markdown 内容的 Base64 编码 |

## 源工程集成模板

### GitHub Actions Workflow (源工程)

```yaml
# .github/workflows/archive-to-droneblog.yml
name: Archive to DroneBlog

on:
  push:
    branches: [main]
    paths:
      - "docs/blog/**"

jobs:
  archive:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Find changed blog posts
        id: changed
        run: |
          FILES=$(git diff --name-only HEAD~1 HEAD | grep "^docs/blog/" || true)
          echo "files=$FILES" >> $GITHUB_OUTPUT

      - name: Send archive request
        if: steps.changed.outputs.files != ''
        run: |
          for file in ${{ steps.changed.outputs.files }}; do
            SLUG=$(basename "$file" .md)
            TITLE=$(grep "^title:" "$file" | sed 's/title: //')
            DATE=$(grep "^date:" "$file" | sed 's/date: //')
            TAGS=$(grep "^tags:" "$file" | sed 's/tags: //')
            CATEGORIES=$(grep "^categories:" "$file" | sed 's/categories: //')
            CONTENT_B64=$(base64 -w 0 "$file")

            curl -X POST \
              -H "Authorization: token ${{ secrets.ARCHIVE_PAT }}" \
              -H "Accept: application/vnd.github.v3+json" \
              https://api.github.com/repos/oldoldtea/oldoldtea.github.io/dispatches \
              -d "{
                \"event_type\": \"archive-blog\",
                \"client_payload\": {
                  \"source_repo\": \"${{ github.repository }}\",
                  \"source_branch\": \"${{ github.ref_name }}\",
                  \"commit_sha\": \"${{ github.sha }}\",
                  \"article_title\": \"$TITLE\",
                  \"article_slug\": \"$SLUG\",
                  \"article_date\": \"$DATE\",
                  \"article_tags\": \"$TAGS\",
                  \"article_categories\": \"$CATEGORIES\",
                  \"content_base64\": \"$CONTENT_B64\"
                }
              }"
          done
```

## DroneBlog 流水线日志格式

归档请求被接收后，DroneBlog 的 `.ai-pipeline.log` 会追加以下记录：

```
# [Archive] Cross-repo pipeline log
[2026-05-20T10:05:00+08:00] [START] [archive] Archive received from oldoldtea/project-a
[2026-05-20T10:05:00+08:00] [INFO] [archive] Source: oldoldtea/project-a@abc123
[2026-05-20T10:05:00+08:00] [INFO] [archive] Article: C++ 并发编程实战
[2026-05-20T10:05:00+08:00] [INFO] [archive] Slug: cpp-concurrency-practice
[2026-05-20T10:05:02+08:00] [OK] [archive] Build verification passed
[2026-05-20T10:05:03+08:00] [OK] [archive] Archive completed and committed
```

## 安全考虑

| 措施 | 说明 |
|------|------|
| PAT 权限最小化 | `ARCHIVE_PAT` 仅授予 `repo` 权限，不开放其他 scope |
| 事件类型白名单 | Workflow 只响应 `archive-blog` 事件类型 |
| 内容校验 | 接收后执行 Front-matter 校验和 hexo generate 构建验证 |
| 来源追溯 | 每篇归档文章在日志和 commit message 中记录源仓库信息 |
