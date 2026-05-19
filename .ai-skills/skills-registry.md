# Skills Registry — Skill 动态注册表

> 本文件面向 AI 编程助手。当任务涉及特定领域知识时，AI 应按本文件定义的流程进行动态 Skill 匹配。
> 核心原则：**用户输入后立即提取关键词 → 本地注册表匹配 → 未匹配则 find-skills 搜索 → 无论结果如何都继续执行**。

---

## 一、动态匹配流程（Dynamic Matching Pipeline）

收到用户请求后，按以下顺序执行，**不可跳过任何步骤**：

```
[用户输入]
    │
    ▼
[Step 1] 关键词提取 —— 从用户请求中提取技术关键词
    │
    ▼
[Step 2] 本地注册表匹配 —— 对照「本地 Skill 映射表」查找匹配项
    │
    ├─ 匹配到 → [Step 4] 加载 Skill
    │
    └─ 未匹配 → [Step 3] find-skills 回退搜索
                    │
                    ├─ 搜索到 → [Step 4] 加载 Skill
                    │
                    └─ 未搜索到 → [Step 5] 记录结果并继续
    │
    ▼
[Step 4] 加载 Skill（如匹配到）
    │
    ▼
[Step 5] 输出匹配结果标记，进入后续阶段
```

> **硬性规则**：
> 1. **Step 3（find-skills 回退搜索）为强制步骤**：只要 Step 2 本地注册表未匹配到 Skill，**必须**执行 Step 3，不允许 AI 以「任务简单」「通用能力足够」等任何理由主观跳过。
> 2. **即使 Step 2 和 Step 3 都未找到任何 Skill**，也必须执行 Step 5 输出「无匹配 Skill」标记，然后继续执行后续流水线阶段。**不允许因未匹配到 Skill 而阻塞或中断任务**。
> 3. **阶段间信号验证**：Skill 识别阶段（skill_match）开始前，必须验证需求分析阶段（analysis）已发送 `[OK] [analysis]` 信号。若信号缺失，标记为流程违规，触发 compliance_audit 阶段重新执行。

---

## 二、关键词提取规则（Keyword Extraction）

### 2.1 提取时机

**必须在收到用户首个请求后立即执行**，在输出任何实质性内容之前完成。

### 2.2 提取方法

从用户请求中识别以下类别的关键词：

| 类别 | 提取目标 | 示例 |
|------|---------|------|
| **技术框架/库** | 编程语言、框架、库的名称 | React, Vue, Kubernetes, Docker, Kafka, Tokio |
| **任务类型** | 用户想要做什么 | 部署, 测试, 优化, 审查, 生成, 解析, 调试 |
| **平台/环境** | 运行环境或目标平台 | Web, Mobile, Cloud, GitHub, AWS, 浏览器 |
| **输出格式** | 期望的产出形式 | 文档, 图表, 代码, 配置, 报告 |

### 2.3 提取示例

| 用户输入 | 提取的关键词 |
|---------|------------|
| "生成一篇关于 k8s 的博客" | `Kubernetes`, `博客/文档` |
| "帮我优化这个 React 组件的性能" | `React`, `性能优化` |
| "审查一下这个页面的可访问性" | `UI审查`, `可访问性` |
| "写一个 Docker 部署脚本" | `Docker`, `部署` |
| "修复 Hexo 构建报错" | `Hexo`, `调试/问题排查` |

---

## 三、本地 Skill 映射表（Local Skill Registry）

以下 Skill 为当前环境已安装，**优先匹配**。匹配时按关键词相似度排序，取最相关的一项或多项。

| 匹配关键词 | 推荐 Skill | 说明 | 优先级 |
|-----------|-----------|------|--------|
| React 组件设计、组合模式、props 清理、compound components | `vercel-composition-patterns` | React 组合模式最佳实践 | P1 |
| React/Next.js 性能优化、数据获取、Bundle 优化、RSC | `vercel-react-best-practices` | React 最佳实践 | P1 |
| React Native、Expo、移动端开发、iOS/Android | `vercel-react-native-skills` | React Native 技能 | P1 |
| UI 审查、可访问性、a11y、UX 规范、设计系统 | `web-design-guidelines` | Web 设计指南 | P1 |
| 找 skill、发现 skill、有没有 skill、skill 搜索 | `find-skills` | 发现可用 skill（仅在用户主动询问时使用） | P2 |
| 创建 skill、新 skill、skill 开发、扩展 AI 能力 | `skill-creator` | Skill 创建指南 | P2 |
| DOCX、Word 文档、.docx 处理 | `anthropics-docx` | DOCX 创建、编辑和分析 | P1 |

> **注意**：此表仅为「已安装 Skill」的子集。如果用户请求涉及的技术领域不在上表中，**必须执行 Step 3 的 find-skills 回退搜索**。

---

## 四、find-skills 回退机制（Fallback Search）

### 4.1 触发条件（强制）

满足以下任一条件时**必须触发**，无例外：
- Step 2（本地注册表匹配）**未找到**任何匹配的 Skill
- 用户请求涉及的技术领域**明显超出**本地注册表覆盖范围
- 用户**明确要求**查找某个领域的 Skill

> ⚠️ **禁止行为**：AI 不得因「任务简单」「通用能力足够」「节省时间」等任何理由跳过本步骤。

### 4.2 执行流程

```bash
# 使用提取的关键词作为查询词
npx skills find {关键词}
```

**示例**：
- 用户说 "帮我写个 Terraform 配置" → 本地无匹配 → 执行 `npx skills find terraform`
- 用户说 "有没有 skill 能帮我做代码审查" → 执行 `npx skills find code review`

### 4.3 结果处理

| 搜索结果 | 处理方式 |
|---------|---------|
| 找到相关 Skill | 向用户展示推荐列表（名称 + 说明 + 安装命令），询问是否加载 |
| 未找到相关 Skill | 输出 `[Skill Match] 未在本地注册表和 skills.sh 生态中找到匹配 Skill`，直接继续执行 |
| 命令执行失败（如网络问题） | 输出 `[Skill Match] find-skills 搜索失败（{原因}），将使用通用能力继续执行` |
| **AI 违规跳过** | 记录为 `[FAIL] [skill_match] find-skills 回退搜索未执行 (流程违规)`，触发 compliance_audit 阶段，从 skill_match 阶段重新开始执行 |

### 4.5 违规重新执行流程（Compliance Re-execution）

当检测到 find-skills 回退搜索被违规跳过时：

1. **立即停止当前所有操作**
2. **写入违规日志**：
   ```
   [YYYY-MM-DDTHH:mm:ss+08:00] [FAIL] [skill_match] 流程违规: find-skills 回退搜索未执行
   [YYYY-MM-DDTHH:mm:ss+08:00] [START] [compliance_audit] 流程合规审核 started
   [YYYY-MM-DDTHH:mm:ss+08:00] [OK] [compliance_audit] 流程合规审核 completed: 检测到 skill_match 阶段违规，触发重新执行
   ```
3. **输出违规通知**：
   ```
   [Pipeline] ⚠️ 流程合规审核检测到违规
   [Pipeline] 违规类型: find-skills 回退搜索未执行（强制性步骤被跳过）
   [Pipeline] 违规阶段: Skill 识别
   [Pipeline] 正在从违规阶段重新执行...
   ```
4. **回到 skill_match 阶段重新执行**：
   - 重新提取关键词
   - 重新扫描本地注册表
   - **强制执行 find-skills 回退搜索**
   - 记录搜索结果
5. **重新执行后必须通过 compliance_audit 验证**
6. **重新执行次数上限**：2 次。超过仍违规则终止任务

### 4.4 用户确认规则

- **匹配到已安装 Skill**：无需用户确认，直接加载（因为已存在于本地环境）
- **匹配到未安装 Skill**：向用户展示并询问是否安装加载
- **用户明确说"不用 skill"或"直接做"**：跳过 Skill 加载，继续执行

---

## 五、加载规则（Loading Rules）

### 5.1 加载执行

确认加载后，读取对应 `SKILL.md` 文件路径：
- User-scope skills：`/home/lz/.claude/skills/{skill-name}/SKILL.md`
- Built-in skills：`/home/lz/.local/share/uv/tools/kimi-cli/lib/python3.13/site-packages/kimi_cli/skills/{skill-name}/SKILL.md`

### 5.2 上下文标记

加载完成后，必须在输出中显式标记：

```
[Skill Loaded: {skill-name}]
```

如果未加载任何 Skill，标记为：

```
[Skill Match] 无匹配 Skill，使用通用能力执行
```

### 5.3 遵守约束

- 已加载 Skill 的规范、示例、约束纳入当前工作上下文
- 若 Skill 规范与 AGENTS.md 冲突，**以 AGENTS.md 为准**
- 若 Skill 规范与 pipeline-executor.md 冲突，**以 pipeline-executor.md 为准**

---

## 六、存储规范

- **存储路径**：项目根目录下的 `.ai-skills/`
- **文件命名**：每个 Skill 一个独立文件，文件名即 Skill 名称，使用 kebab-case
- **单文件 = 单 Skill**：禁止在一个 `.md` 文件中定义多个 Skill
- **多 Skill 并行**：允许同时加载多个 Skill，加载顺序按匹配优先级或用户确认顺序
- **Git 隔离**：`.ai-skills/` 目录已被 `.gitignore` 排除，不参与版本控制
- **构建隔离**：`.ai-skills/` 目录不在 Hexo 的 `source/` 或 `themes/` 路径下，不参与静态站点构建

---

## 七、快速参考：常见技术领域 → 搜索关键词对照

| 用户提到的技术 | find-skills 查询关键词 |
|--------------|----------------------|
| Kubernetes / k8s / 容器编排 | `kubernetes`, `container`, `devops` |
| Docker / 容器化 | `docker`, `container` |
| Terraform / IaC | `terraform`, `infrastructure` |
| CI/CD / 流水线 | `cicd`, `pipeline`, `github-actions` |
| 测试 / 单元测试 / E2E | `testing`, `jest`, `playwright` |
| 数据库 / SQL / ORM | `database`, `sql`, `prisma` |
| API / REST / GraphQL | `api`, `graphql`, `openapi` |
| 安全 / 漏洞扫描 | `security`, `vulnerability` |
| 日志 / 监控 / 可观测性 | `observability`, `monitoring`, `logging` |
| 文档 / README / 变更日志 | `documentation`, `readme`, `changelog` |

> 上表仅作参考。实际执行时以 Step 2 提取的关键词为准。
