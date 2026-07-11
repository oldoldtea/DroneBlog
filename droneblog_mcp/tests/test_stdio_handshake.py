"""stdio 协议握手集成测试（端到端）。

以子进程真实启动 ``droneblog-mcp serve --transport stdio``，喂入 JSON-RPC
initialize / tools/list / resources/list / resources/templates/list，然后断言：

1. stdout 的**每一行**都是合法 JSON-RPC（无任何启动横幅泄漏到 stdout）；
2. tools/list 返回 ≥15 个工具，含 setup_init/blog_generate 等；
3. resources/list 含 blogs://list（collection，避免与 blog://{slug} 冲突）；
4. resources/templates/list 含 blog://{slug}。

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


def test_stdio_handshake_no_stdout_pollution():
    env = os.environ.copy()
    env["DRONEBLOG_DIR"] = str(REPO_ROOT)
    # 子进程 stdout/stderr 以 UTF-8 写入，匹配父进程解码，避免中文乱码/解码异常
    env["PYTHONIOENCODING"] = "utf-8"
    env.setdefault("PYTHONUNBUFFERED", "1")

    messages = [
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
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "resources/list"},
        {"jsonrpc": "2.0", "id": 4, "method": "resources/templates/list"},
    ]
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
            cwd=str(REPO_ROOT),
        )
    except FileNotFoundError:
        pytest.skip("未安装 droneblog-mcp 且无法以 python -m 启动")

    stderr_lines: list[str] = []
    threading.Thread(target=_drain, args=(proc.stderr, stderr_lines), daemon=True).start()

    assert proc.stdin is not None and proc.stdout is not None
    proc.stdin.write(payload)
    proc.stdin.flush()

    # 逐条读取响应，直到拿齐全部 id 或超时；保持 stdin 开启避免 shutdown 竞态丢包
    parsed: list[dict] = []
    expected_ids = {1, 2, 3, 4}
    by_id: dict[int, dict] = {}
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
        except json.JSONDecodeError as e:
            proc.stdin.close()
            proc.kill()
            pytest.fail(f"stdout 出现非 JSON-RPC 输出（协议污染）: {ln!r}\n错误: {e}")
        parsed.append(obj)
        if isinstance(obj, dict) and "id" in obj:
            by_id[obj["id"]] = obj

    proc.stdin.close()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()

    assert parsed, "server 无任何 stdout 输出。stderr=\n" + "\n".join(stderr_lines[-40:])

    # 关键断言：握手的 4 个响应都必须回来且无 error
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
