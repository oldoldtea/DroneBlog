"""stdio 协议握手集成测试（端到端）。

以子进程真实启动 ``droneblog-mcp serve --transport stdio``，喂入 JSON-RPC
initialize / tools/list / resources/list / resources/templates/list，然后断言：

1. stdout 的**每一行**都是合法 JSON-RPC（无任何启动横幅泄漏到 stdout）；
2. tools/list 返回 ≥15 个工具，含 setup_init/blog_generate 等；
3. resources/list 含 blogs://list（collection，避免与 blog://{slug} 冲突）；
4. resources/templates/list 含 blog://{slug}；
5. 从**非博客目录**启动时 ``DRONEBLOG_DIR`` 环境变量必须生效（回归：
   --dir 默认 None，不得用 cwd 覆盖环境变量），blog_list 能读到真实文章。

实现要点：使用 ``Popen`` 保持 stdin 开启并逐条 ``readline`` 排空响应，再关闭
stdin。若用一次性 ``subprocess.run(input=...)``，写完即 EOF 会触发服务器在
最后一个响应尚未刷出 stdout 时关闭，导致最后一个 id 偶发丢失（shutdown 竞态，
与真实长连接客户端行为不同）。同时设 ``PYTHONIOENCODING=utf-8`` 让子进程的
中文描述以 UTF-8 写入管道，避免 Windows 控制台代码页（cp936）与父进程解码
不一致。
"""

import json
import os
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _server_cmd():
    """优先用安装后的 console script，其次退化为 ``python -m``。"""
    exe = shutil.which("droneblog-mcp")
    if exe:
        return [exe, "serve", "--transport", "stdio"]
    return [sys.executable, "-m", "droneblog_mcp", "serve", "--transport", "stdio"]


def _drain(stream, sink: list[str]) -> None:
    for ln in stream:
        sink.append(ln.rstrip("\n"))


def _run_session(messages: list[dict], cwd: str, expected_ids: set[int]):
    """启动 server、写入消息、逐条读回响应。

    Returns:
        (by_id, non_json_lines, stderr_lines)
    """
    env = os.environ.copy()
    env["DRONEBLOG_DIR"] = str(REPO_ROOT)
    # 子进程 stdout/stderr 以 UTF-8 写入，匹配父进程解码，避免中文乱码/解码异常
    env["PYTHONIOENCODING"] = "utf-8"
    env.setdefault("PYTHONUNBUFFERED", "1")

    payload = "\n".join(json.dumps(m, ensure_ascii=False) for m in messages) + "\n"

    try:
        proc = subprocess.Popen(
            _server_cmd(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            env=env,
            cwd=cwd,
        )
    except FileNotFoundError:
        pytest.skip("未安装 droneblog-mcp 且无法以 python -m 启动")

    stderr_lines: list[str] = []
    threading.Thread(target=_drain, args=(proc.stderr, stderr_lines), daemon=True).start()

    assert proc.stdin is not None and proc.stdout is not None
    proc.stdin.write(payload)
    proc.stdin.flush()

    # 逐条读取响应，直到拿齐全部 id 或超时；保持 stdin 开启避免 shutdown 竞态丢包
    by_id: dict[int, dict] = {}
    non_json: list[str] = []
    deadline = time.time() + 20
    while not expected_ids.issubset(by_id) and time.time() < deadline:
        ln = proc.stdout.readline()
        if not ln:
            break  # 服务器已退出
        ln = ln.strip()
        if not ln:
            continue
        try:
            obj = json.loads(ln)
        except json.JSONDecodeError:
            non_json.append(ln)
            continue
        if isinstance(obj, dict) and "id" in obj:
            by_id[obj["id"]] = obj

    proc.stdin.close()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()

    return by_id, non_json, stderr_lines


def _init_msgs() -> list[dict]:
    return [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "pytest", "version": "0"},
            },
        },
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
    ]


def test_stdio_handshake_no_stdout_pollution():
    by_id, non_json, stderr_lines = _run_session(
        _init_msgs()
        + [
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "resources/list"},
            {"jsonrpc": "2.0", "id": 4, "method": "resources/templates/list"},
        ],
        cwd=str(REPO_ROOT),
        expected_ids={1, 2, 3, 4},
    )

    # 关键断言：stdout 每一行都必须是合法 JSON（捕获横幅/print 污染）
    assert not non_json, f"stdout 出现非 JSON-RPC 输出（协议污染）: {non_json[:3]}"
    assert by_id, "server 无任何 stdout 输出。stderr=\n" + "\n".join(stderr_lines[-40:])

    # 握手的 4 个响应都必须回来且无 error
    for rid in (1, 2, 3, 4):
        assert rid in by_id, (
            f"缺少 id={rid} 的 JSON-RPC 响应，已收到: {sorted(by_id)}\n"
            f"stderr 尾部:\n" + "\n".join(stderr_lines[-40:])
        )
        assert "error" not in by_id[rid], f"id={rid} 返回错误: {by_id[rid].get('error')}"

    tools = by_id[2]["result"]["tools"]
    tool_names = {t["name"] for t in tools}
    assert len(tools) >= 15, f"工具数量不足: {len(tools)}"
    for must in ("setup_init", "blog_generate", "blog_list", "build", "deploy", "pipeline_run"):
        assert must in tool_names, f"缺少工具 {must}"

    resources = by_id[3]["result"]["resources"]
    resource_uris = {r["uri"] for r in resources}
    assert "blogs://list" in resource_uris, f"缺少 blogs://list，实际: {resource_uris}"

    templates = by_id[4]["result"].get("resourceTemplates", [])
    template_uris = {t["uriTemplate"] for t in templates}
    assert any(u.startswith("blog://") and "{slug}" in u for u in template_uris), (
        f"缺少 blog://{{slug}} 模板，实际: {template_uris}"
    )


def test_serve_respects_droneblog_dir_from_other_cwd(tmp_path):
    """回归：从非博客目录启动时 DRONEBLOG_DIR 必须生效。

    --dir 默认 None，不能用 cwd 覆盖环境变量；否则 MCP 客户端在任意目录
    拉起 server 时博客目录会错指到 cwd，blog_list 读不到文章。
    """
    by_id, non_json, stderr_lines = _run_session(
        _init_msgs()
        + [
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "blog_list", "arguments": {"limit": 5}},
            },
        ],
        cwd=str(tmp_path),  # 故意用非博客目录作 cwd
        expected_ids={1, 2},
    )

    assert not non_json, f"stdout 出现非 JSON-RPC 输出: {non_json[:3]}"
    assert 2 in by_id, "blog_list 无响应。stderr 尾部:\n" + "\n".join(stderr_lines[-40:])
    result = by_id[2].get("result", {})
    assert not result.get("isError"), f"blog_list 调用失败: {result}"

    # FastMCP 对 list 返回：structuredContent.result 为完整列表，
    # content 则每项一个 TextContent 块。以 structuredContent 为准。
    posts = (result.get("structuredContent") or {}).get("result")
    assert isinstance(posts, list) and len(posts) > 0, (
        "blog_list 读到 0 篇文章——DRONEBLOG_DIR 未生效（疑似被 --dir 默认值覆盖）。"
        f"result={str(result)[:300]}"
    )
    assert posts[0].get("slug"), f"文章缺 slug 字段: {posts[0]}"
