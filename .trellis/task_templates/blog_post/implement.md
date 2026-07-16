# Implement Plan: 写一篇博客

## Implementation Checklist

1. **需求确认**
   - [ ] 确认文章标题、技术主题、内容类型、分类、标签。
   - [ ] 若用户未指定，提供推荐选项并等待确认。

2. **文件名生成**
   - [ ] 按 `{技术名缩写}-{内容主题}-{内容类型}.md` 生成文件名。
   - [ ] 检查文件名是否为 ASCII 小写、短横线连接、无空格/下划线/中文。

3. **生成文章**
   - [ ] 使用 `blog_generate` 工具生成 Markdown 到 `source/_posts/`。
   - [ ] 或先通过 `prompts/blog_writing` 获取大纲，用户确认后再生成正文。

4. **文章校验**
   - [ ] 使用 `blog_read` 读取文件，确认 Front-matter 正确。
   - [ ] 检查 `categories` 在 6 选 1 白名单内。
   - [ ] 检查 `tags` 数量为 2-3 个。

5. **构建验证**
   - [ ] 运行 `build`（等价于 `hexo clean && hexo generate`）。
   - [ ] 检查无错误、无缺失资源警告。

6. **安全与日志**
   - [ ] 使用 `scan_sensitive_info` 检查新增文件无敏感信息。
   - [ ] 在 `.ai-pipeline.log` 中追加阶段信号。

7. **输出汇报**
   - [ ] 按 `pipeline-config.yml` 输出模板汇报：摘要、文件清单、验证结果、后续建议。

## Validation Commands

```bash
# 构建验证（MCP build 工具内部已执行，可手动复核）
hexo clean && hexo generate

# 敏感信息扫描（MCP 工具内部已执行，可手动复核）
grep -R -E "api[_-]?key|token|password|secret|private[_-]?key" source/_posts/
```

## Rollback

- 若构建失败，根据日志修复文章或 Front-matter；无法修复则删除新生成的文件并重新生成。
- 删除命令：手动移除 `source/_posts/` 下对应文件，然后重新运行 `hexo clean && hexo generate`。

## Output Template

```markdown
## 修改摘要

撰写并验证了一篇关于 {技术主题} 的博客文章。

## 文件清单

| operation | path |
|-----------|------|
| add | source/_posts/{filename}.md |

## 验证结果

- 文件名规范：✅
- Front-matter 规范：✅
- 分类/标签白名单：✅
- Hexo 构建：✅
- 敏感信息扫描：✅

## 已加载 Skill / Prompt

- blog_writing
- tech_analysis（如使用）

## 后续建议

- 本地预览：`hexo server`
- 部署：`hexo deploy`（需用户确认）
```
