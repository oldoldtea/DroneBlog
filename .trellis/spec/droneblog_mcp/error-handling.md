# droneblog_mcp — 错误处理与用户消息

> 约定如何分类异常、如何向用户呈现错误、如何保护敏感信息，以及日志记录约束。

---

## 1. 异常分类

所有 MCP 工具内部抛出的异常应归到以下三类之一：

| 类别 | 含义 | 用户消息语言 | 示例 |
|------|------|--------------|------|
| `UserError` | 用户输入或环境配置错误 | 中文，友好，可操作 | 文件不存在、参数缺失、分类不在白名单 |
| `SystemError` | 项目环境或外部命令错误 | 中文，说明原因 | hexo 未安装、Node 环境异常、网络失败 |
| `InternalError` | 代码内部错误 / 未预期异常 | 中文，简洁；详情进日志 | 空指针、索引越界、序列化失败 |

### 1.1 使用方式

```python
class UserError(Exception):
    """用户可修复的错误。"""

class SystemError(Exception):
    """环境或外部依赖错误。"""

class InternalError(Exception):
    """代码内部错误。"""
```

- 工具函数内部捕获异常后，统一包装成标准返回结构。
- 不要直接让未捕获异常冒泡到 MCP 客户端，避免暴露内部路径或堆栈。

---

## 2. 用户错误消息

### 2.1 消息原则

- 使用**简体中文**。
- 直接说明问题，给出可执行的下一步。
- 不要包含文件绝对路径、堆栈、环境变量名。
- 不要包含脱敏前的密钥。

### 2.2 示例

| 场景 | 推荐消息 | 不推荐消息 |
|------|----------|------------|
| 分类不在白名单 | `"分类必须是：后端开发、前端技术、系统编程、云原生、人工智能、分布式系统"` | `"Category invalid"` |
| 文件不存在 | `"文章文件不存在：cpp-core-features.md"` | `"FileNotFoundError: [Errno 2] No such file or directory: C:\\Users\\..."` |
| 构建失败 | `"Hexo 构建失败，请检查 source/_posts/ 下文章格式或运行 hexo generate --debug"` | `"hexo process exited with code 1: Traceback..."` |
| API Key 缺失 | `"缺少 KIMI_API_KEY 环境变量，请在 .env 中配置后重试"` | `"KIMI_API_KEY is None"` |

---

## 3. 密钥脱敏

### 3.1 脱敏规则

- 任何从环境变量读取的密钥，在日志、工具结果、错误消息中显示时：
  - 显示前 4 位 + `...` + 最后 2 位（或仅前 4 位 + `...`）。
  - 长度不足 6 位时显示 `***`。

```python
import re

def redact_secret(value: str | None) -> str:
    if not value:
        return "<unset>"
    if len(value) <= 6:
        return "***"
    return f"{value[:4]}...{value[-2:]}"
```

### 3.2 检查点

- 工具返回的 JSON 中不应包含 `api_key`、`token`、`secret`、`password` 等键的原始值。
- 命令行参数中不要传递密钥（避免 `ps` 泄露）。
- 测试断言中比较密钥时，比较脱敏后的值或仅检查是否非空。

---

## 4. 日志约束

### 4.1 日志格式

`.ai-pipeline.log` 格式：

```text
[{timestamp}] [{status}] [{stage}] {message}
```

- `timestamp`：`YYYY-MM-DD HH:mm:ss` 或 ISO 8601。
- `status`：`START` / `OK` / `FAIL` / `ROLLBACK` / `ABORT`。
- `stage`：`analysis` / `skill_match` / `execute` / `compliance_audit` / `security` / `output`。
- `message`：简洁、无密钥、无堆栈。

### 4.2 日志内容示例

```text
[2026-07-16 10:00:00] [START] [analysis] 用户请求：写一篇 Kafka 源码解析
[2026-07-16 10:00:05] [OK] [analysis] 任务类型：content_creation
[2026-07-16 10:00:06] [OK] [skill_match] 使用 blog_writing prompt
[2026-07-16 10:00:30] [OK] [execute] 生成文章 kafka-message-transmission.md
[2026-07-16 10:00:35] [FAIL] [execute] Hexo 构建失败：YAML 语法错误
[2026-07-16 10:00:36] [ROLLBACK] [execute] 回滚至上一版本
```

### 4.3 日志 vs 错误返回

- 日志：给开发者/审计使用，可含技术细节（不含密钥）。
- 工具返回：`message` 给用户，应简洁友好。

---

## 5. 错误处理模板

```python
from droneblog_mcp.errors import UserError, SystemError, InternalError
from droneblog_mcp.utils.redaction import redact_secret

async def some_tool(path: Path) -> dict:
    try:
        if not path.exists():
            raise UserError(f"文件不存在：{path.name}")
        result = await run_external_process(path)
        return {
            "success": True,
            "message": "操作成功",
            "data": result,
            "error": None,
        }
    except UserError as e:
        return {"success": False, "message": str(e), "data": None, "error": {"code": "USER_ERROR", "detail": str(e)}}
    except SystemError as e:
        log.error(f"System error: {e}")
        return {"success": False, "message": str(e), "data": None, "error": {"code": "SYSTEM_ERROR", "detail": str(e)}}
    except Exception as e:
        log.exception("Unexpected internal error")
        return {"success": False, "message": "内部错误，请查看日志", "data": None, "error": {"code": "INTERNAL_ERROR", "detail": type(e).__name__}}
```
