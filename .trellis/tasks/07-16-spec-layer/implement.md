# Implement Plan: `.trellis/spec` 规范层与博客任务模板

## Implementation Checklist

1. **创建目录结构**
   - [ ] `mkdir -p .trellis/spec/guides .trellis/spec/droneblog_mcp .trellis/task_templates/blog_post`

2. **编写通用指南**
   - [ ] `.trellis/spec/guides/index.md`
     - 提交规范（简体中文前缀）
     - 文档风格（UTF-8、LF、Markdown）
     - 安全基线（密钥不提交、token 脱敏）
     - AI 工作流加载顺序

3. **编写 droneblog_mcp 包规范**
   - [ ] `.trellis/spec/droneblog_mcp/index.md`（入口 + checklist + quality check）
   - [ ] `.trellis/spec/droneblog_mcp/conventions.md`
   - [ ] `.trellis/spec/droneblog_mcp/error-handling.md`
   - [ ] `.trellis/spec/droneblog_mcp/testing.md`
   - [ ] `.trellis/spec/droneblog_mcp/ai-workflow.md`

4. **编写博客任务模板**
   - [ ] `.trellis/task_templates/blog_post/prd.md`
   - [ ] `.trellis/task_templates/blog_post/implement.md`

5. **验证**
   - [ ] `python ./.trellis/scripts/get_context.py --mode packages` 发现新 spec 层
   - [ ] 无 maple 等过时字符串
   - [ ] Markdown/YAML 语法无误

## Validation Commands

```bash
python ./.trellis/scripts/get_context.py --mode packages
grep -R "hexo-theme-maple" .trellis/spec || true
```

## Rollback

删除 `.trellis/spec/` 和 `.trellis/task_templates/` 即可回滚。
