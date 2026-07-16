# 写一篇博客：{文章标题}

## Goal

撰写一篇关于 **{技术主题}** 的博客文章，并发布到 DroneBlog 的 `source/_posts/` 目录下，经过构建验证后可供部署。

## Background

- 本任务使用 `droneblog_mcp` 的 MCP 工具生成/校验博客内容。
- 文章遵循项目 Front-matter 规范、文件名规范与分类/标签白名单。
- 构建验证通过 `hexo clean && hexo generate` 完成。

## Requirements

### R1 — 文章信息确认

- 标题：`{文章标题}`
- 技术主题：`{技术主题}`
- 内容类型：{深度解析 / 入门教程 / 实践笔记 / 源码解析 / 其他}
- 目标分类：`{后端开发 / 前端技术 / 系统编程 / 云原生 / 人工智能 / 分布式系统}`（6 选 1）
- 目标标签：2-3 个，第 1 个为核心技术/语言，第 2 个为主题方向，第 3 个为可选细分领域

### R2 — 文件名规范

- 文件名格式：`{技术名缩写}-{内容主题}-{内容类型}.md`
- 小写、短横线连接、ASCII 字符，无空格、无中文、无下划线、无驼峰。
- 示例：`cpp-core-features.md`、`kafka-message-transmission.md`。

### R3 — Front-matter 规范

```yaml
---
title: {文章标题}
date: {YYYY-MM-DD HH:mm:ss}
tags:
  - {核心技术/语言}
  - {主题方向}
  - {细分领域（可选）}
categories:
  - {6 选 1}
---
```

### R4 — 内容质量

- 正文使用简体中文，技术术语可保留英文。
- 结构清晰，包含标题、引言、正文、总结。
- 代码块使用正确语言标注，关键代码附带注释。
- 图片使用相对路径或可信外部图床，避免隐私/版权风险。

### R5 — 构建验证

- 生成文章后执行 `hexo clean && hexo generate`。
- 构建无报错，无缺失资源警告。

## Acceptance Criteria

- [ ] `source/_posts/` 下存在符合命名规范的文件。
- [ ] 文件包含正确的 Front-matter（title、date、tags、categories）。
- [ ] 分类在 6 个白名单内，标签数量为 2-3 个。
- [ ] `hexo clean && hexo generate` 成功完成。
- [ ] `.ai-pipeline.log` 中记录了阶段信号（analysis / skill_match / execute / security / output）。
- [ ] 工具返回结果中未泄露任何密钥或敏感信息。

## Out of Scope

- 不执行部署（除非用户明确要求）。
- 不修改主题模板或 `_config.kratos-rebirth.yml`。
- 不修改已发布的其他文章。

## Notes

- 若用户对标题/大纲有偏好，先确认再生成正文。
- 生成过程中如遇构建失败，根据日志定位问题并修复，必要时回滚。
