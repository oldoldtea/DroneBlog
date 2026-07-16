# droneblog_mcp — 测试规范

> 约定 `droneblog_mcp` 包的测试结构、夹具、接口矩阵和 SSE 烟测。

---

## 1. 测试结构

```
droneblog_mcp/tests/
├── conftest.py              # 共享 fixture、mock、常量
├── test_validators.py       # 输入校验与工具参数校验
├── test_packaging.py        # 包结构与入口检查
├── test_stdio_handshake.py  # stdio 传输握手与生命周期
└── test_logic_regressions.py # 端到端逻辑回归（接口矩阵、SSE 烟测等）
```

- 一个测试文件对应一个功能领域，避免单文件过大。
- 测试函数名清晰：`test_` + `被测功能` + `场景` + `预期结果`。

```python
def test_blog_generate_with_valid_input_creates_file(tmp_path):
    ...

def test_config_set_rejects_invalid_yaml(monkeypatch):
    ...
```

---

## 2. 共享夹具（conftest.py）

### 2.1 推荐 fixture

```python
import pytest
from pathlib import Path

@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    """提供临时项目根目录。"""
    return tmp_path

@pytest.fixture
def sample_post(project_root: Path) -> Path:
    """返回一篇样例文章路径。"""
    post_dir = project_root / "source" / "_posts"
    post_dir.mkdir(parents=True)
    post = post_dir / "cpp-core-features.md"
    post.write_text("---\ntitle: C++ 核心特性\ndate: 2026-07-16 10:00:00\n---\n", encoding="utf-8")
    return post

@pytest.fixture
def mock_env(monkeypatch):
    """提供隔离的环境变量。"""
    monkeypatch.setenv("KIMI_API_KEY", "kimi-fake-key-for-tests")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake-key-for-tests")
```

### 2.2 不要做的事

- 不要在测试中写入真实项目目录（`source/_posts/`）。
- 不要调用真实的外部 API（OpenAI / Kimi / GitHub）。使用 `respx`/`responses` 或 `monkeypatch` mock。
- 不要提交真实密钥到测试文件。

---

## 3. 测试覆盖要求

### 3.1 最小覆盖

| 类型 | 覆盖要求 |
|------|----------|
| 工具函数 | 正常路径 + 参数校验失败 + 外部命令失败 |
| 配置读写 | 存在/不存在、合法 YAML、非法 YAML |
| 文件操作 | 文件存在、文件不存在、权限异常 |
| 构建/部署 | 成功、失败、命令未找到 |
| 资源 | 返回格式、过滤、错误处理 |
| Prompts | 模板渲染、变量注入 |
| 脱敏 | 长密钥、短密钥、空密钥 |

### 3.2 接口矩阵

当前目标：15 Tools × 5 Resources × 3 Prompts = 至少 51 个接口点需验证。

- 每个 tool 至少有一个测试用例覆盖其主路径。
- 每个 resource 至少有一个测试用例覆盖其返回结构。
- 每个 prompt 至少有一个测试用例覆盖其模板渲染。

---

## 4. SSE 烟测

### 4.1 目的

验证 MCP Server 通过 SSE 传输时能正常启动、接收请求、返回结果。

### 4.2 推荐方式

使用 `pytest` + `httpx` 或 `mcp.client.sse` 在临时端口启动 server：

```python
import pytest
import httpx

@pytest.mark.asyncio
async def test_sse_server_smoke():
    # 在随机端口启动 server
    # 通过 SSE 端点发送 tools/list 请求
    # 断言返回包含 15 个 tools
```

### 4.3 检查点

- Server 能正常启动且不阻塞。
- `tools/list` 返回 15 个工具（或当前实际数量）。
- `resources/list` 返回 5 个资源（或当前实际数量）。
- `prompts/list` 返回 3 个 prompts（或当前实际数量）。
- 调用一个 tool 后返回标准 `{success, message, data, error}` 结构。

---

## 5. 测试运行命令

```bash
# 全部测试（在 droneblog_mcp 目录执行）
cd droneblog_mcp
pytest

# 代码风格
ruff check .
```

---

## 6. 新增测试原则

- 修改工具函数 → 同步修改/新增对应测试。
- 新增 tool/resource/prompt → 必须新增至少一个测试。
- 修复 bug → 先写能复现 bug 的测试，再修复，确保测试通过。
