# droneblog_mcp — 代码与 MCP 约定

> 修改 `droneblog_mcp/` 代码前必读。覆盖 Python 命名、类型提示、工具参数设计、返回格式等。

---

## 1. Python 代码风格

### 1.1 命名

| 类型 | 规范 | 示例 |
|------|------|------|
| 模块 | 小写 + 下划线 | `blog_manager.py`, `fs_utils.py` |
| 类 | 大驼峰 | `BlogGenerator`, `ConfigManager` |
| 函数 | 小写 + 下划线 | `generate_blog_post()`, `get_config_value()` |
| 常量 | 大写 + 下划线 | `MAX_TITLE_LENGTH`, `DEFAULT_CATEGORY` |
| 私有成员 | 下划线前缀 | `_internal_helper()`, `_cache` |
| MCP 工具名 | 小写 + 下划线 | `blog_generate`, `config_get`, `build` |
| Pydantic 模型 | 大驼峰 | `BlogPostInput`, `BuildResult` |

### 1.2 类型提示

- 所有函数参数和返回值必须加类型提示（Python 3.10+）。
- 优先使用 `|` 联合类型，少用 `typing.Union`。
- 对可能为 `None` 的返回值使用 `| None`。
- 复杂数据结构使用 `TypedDict` 或 Pydantic `BaseModel`。

```python
from pathlib import Path

def read_post(path: Path) -> str | None:
    ...

def list_posts(directory: Path) -> list[Path]:
    ...
```

### 1.3 导入顺序

```python
# 1. 标准库
import os
from pathlib import Path

# 2. 第三方
from fastmcp import FastMCP
from pydantic import BaseModel

# 3. 本项目
from droneblog_mcp.utils.fs import safe_read
from droneblog_mcp.models import BlogPost
```

---

## 2. MCP 工具设计

### 2.1 工具命名

- 动词优先，语义清晰，避免缩写。
- 同类工具使用一致前缀：
  - 博客操作：`blog_*`（`blog_generate`, `blog_list`, `blog_read`, `blog_edit`, `blog_delete`）
  - 配置操作：`config_*`（`config_get`, `config_set`）
  - 流水线：`pipeline_*`（`pipeline_run`, `pipeline_status`）
  - 站点操作：`build`, `deploy`
  - 初始化/同步：`setup_*`（`setup_init`, `setup_status`, `setup_sync_posts`, `setup_update_config`）

### 2.2 参数设计

- 使用 Pydantic 模型或显式函数参数定义工具参数，避免 `**kwargs`。
- 必填参数放前面，可选参数给出默认值。
- 文件路径参数使用 `Path` 类型，并在函数内部做存在性检查。
- 枚举类值使用 `Literal` 或 Pydantic `Enum`。

```python
from pydantic import BaseModel, Field
from typing import Literal

class BlogGenerateInput(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    category: Literal["后端开发", "前端技术", "系统编程", "云原生", "人工智能", "分布式系统"]
    tags: list[str] = Field(default_factory=list, max_length=3)
```

### 2.3 返回格式

- 工具返回统一为结构化 JSON 字符串（FastMCP 自动序列化）。
- 返回结构至少包含以下字段：

```json
{
  "success": true,
  "message": "用户可读的简短说明",
  "data": { ... },
  "error": null
}
```

- 失败时 `success` 为 `false`，`error` 包含错误码和详情，`message` 给用户友好提示。
- 避免在 `data` 中返回原始堆栈；堆栈写入日志。

### 2.4 文档字符串

- 每个工具函数必须有 docstring，描述功能、参数、返回值、可能的错误。
- 使用 Google 风格或 NumPy 风格均可，但包内保持一致。

```python
async def build() -> dict:
    """执行 Hexo 构建。

    Returns:
        dict: 包含 success、message、data 的标准结果。

    Raises:
        HexoBuildError: 当 hexo generate 返回非零退出码时。
    """
```

---

## 3. 配置与常量

### 3.1 环境变量

- 所有外部密钥（OpenAI API Key、Kimi API Key、Algolia API Key、Git token 等）必须从环境变量读取。
- 不要在代码中硬编码默认值；可使用 `os.environ.get("KEY")` 并在缺失时抛出明确错误。

### 3.2 项目路径

- 使用 `pathlib.Path` 处理路径，避免字符串拼接。
- 对相对路径，以项目根目录为锚点，使用 `Path(__file__).resolve().parents[N]` 或传入的 `project_root`。

### 3.3 常量提取

- 白名单（如分类、标签数限制）提取到模块级常量，避免魔法值散落。

```python
VALID_CATEGORIES = [
    "后端开发",
    "前端技术",
    "系统编程",
    "云原生",
    "人工智能",
    "分布式系统",
]
MAX_TAGS = 3
```

---

## 4. 代码组织

### 4.1 目录结构

```
droneblog_mcp/
├── src/droneblog_mcp/
│   ├── __init__.py
│   ├── server.py          # FastMCP 实例注册入口（tools/resources/prompts 注册）
│   ├── tools/             # 工具函数（按领域分子模块：blog、config、pipeline、build、setup）
│   ├── core/              # 核心业务逻辑（generator、deploy、pipeline、setup）
│   ├── models/            # 共享 Pydantic 模型（blog、config、user_config）
│   └── utils/             # 工具函数（fs、yaml、log、github_client 等）
└── tests/                 # 测试（conftest.py + 各领域测试文件）
    ├── conftest.py
    ├── test_validators.py
    ├── test_packaging.py
    ├── test_stdio_handshake.py
    └── test_logic_regressions.py
```

### 4.2 文件职责

- `server.py` 只负责注册 tools/resources/prompts，不实现业务逻辑；resources 和 prompts 当前在 `server.py` 中内联注册。
- 工具函数放在 `tools/` 下，按领域分文件（如 `blog.py`, `config.py`, `pipeline.py`）。
- 共享逻辑放在 `utils/` 下，避免重复。
- 业务逻辑放在 `core/` 下，被 `tools/` 调用。

---

## 5. 与现有代码的兼容性

- 新工具/资源不应破坏现有 15/5/3 接口。
- 重命名或修改参数属于破坏性变更，必须经父任务评估并在 `AGENTS.md` 中记录迁移指南。
