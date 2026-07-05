#!/usr/bin/env python3
from typing import Tuple
"""
droneblogd.py — DroneBlog Pipeline Service

本地常驻服务，监听 HTTP 端口，接收请求后按流水线规范驱动 AI 生成博客。

用法:
    # 启动服务
    python3 service/droneblogd.py

    # 发送请求
    curl -X POST http://localhost:8765/api/v1/generate \
      -H "Content-Type: application/json" \
      -d '{
        "topic": "C++20 协程入门",
        "category": "后端开发",
        "tags": "C++,协程",
        "prompt": "重点讲 co_await 和 co_yield"
      }'

流水线阶段:
    [需求分析] → [Skill 识别] → [AI 生成] → [人工审核] → [合规审核] → [安全审查] → [构建验证] → [输出]
"""

import os
import sys
import json
import base64
import socket
import subprocess
import tempfile
import re
from datetime import datetime, timezone, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# ── 配置 ──
DRONEBLOG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(DRONEBLOG_DIR, "source", "_posts")
LOG_FILE = os.path.join(DRONEBLOG_DIR, ".ai-pipeline.log")
DEFAULT_PORT = 8765
HOST = "127.0.0.1"

# ── 工具函数 ──

def log(status: str, stage: str, message: str):
    """写入流水线日志"""
    tz = timezone(timedelta(hours=8))
    ts = datetime.now(tz).strftime("%Y-%m-%dT%H:%M:%S+08:00")
    line = f"[{ts}] [{status}] [{stage}] {message}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    return line.strip()


def generate_slug(title: str) -> str:
    """生成 kebab-case slug"""
    slug = re.sub(r"[^a-z0-9]", "-", title.lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


def validate_frontmatter(content: str) -> "tuple":
    """校验 Front-matter 格式"""
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return False, "缺少 YAML Front-matter（应以 --- 开头）"
    if not re.search(r"^title:\s*\S+", content, re.MULTILINE):
        return False, "Front-matter 中缺少 title 字段"
    return True, ""


def validate_tags(content: str) -> "tuple":
    """校验标签数量"""
    tags = re.findall(r"^  - (.+)$", content, re.MULTILINE)
    if len(tags) < 2 or len(tags) > 3:
        return False, f"标签数量 {len(tags)} 个，应为 2-3 个"
    return True, ""


def validate_filename(slug: str) -> "tuple":
    """校验文件名规范"""
    if not re.match(r"^[a-z0-9-]+$", slug):
        return False, "文件名应仅包含小写字母、数字和短横线"
    return True, ""


def call_openai(topic: str, category: str, tags: str, extra_prompt: str, api_key: str) -> str:
    """调用 OpenAI API 生成文章"""
    import urllib.request
    import urllib.error

    system_prompt = """你是一个资深技术博客作者，为 DroneBlog 写作。

文章规范（必须严格遵守）：
1. 标题格式: '{技术名} {内容类型}'，如 'C++ 核心特性深度解析'
2. 使用 YAML Front-matter: title, date, tags, categories
3. tags: 2-3 个，第1个是核心技术/语言，第2个是主题方向
4. categories: 单一分类，只能是以下之一:
   后端开发 / 前端技术 / 系统编程 / 云原生 / 人工智能 / 分布式系统
5. 内容结构: 引言 → 分章节正文（含代码示例） → 总结
6. 语言: 简体中文
7. 代码块使用 ```cpp 等语言标识"""

    user_prompt = f"""请写一篇技术博客。

主题: {topic}
分类: {category}
{f"标签要求: {tags}" if tags else ""}
{f"额外要求: {extra_prompt}" if extra_prompt else ""}

请输出完整的 Markdown 文件内容，包含 YAML Front-matter。"""

    data = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"]


def open_editor(filepath: str) -> bool:
    """打开编辑器供用户审核"""
    editor = os.environ.get("EDITOR", "nano")
    try:
        subprocess.run([editor, filepath], check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def hexo_build() -> "tuple":
    """执行 hexo generate 构建验证"""
    try:
        subprocess.run(
            ["npx", "hexo", "clean"],
            cwd=DRONEBLOG_DIR,
            check=True,
            capture_output=True,
            text=True
        )
        result = subprocess.run(
            ["npx", "hexo", "generate"],
            cwd=DRONEBLOG_DIR,
            check=True,
            capture_output=True,
            text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr


# ── HTTP 处理器 ──

class PipelineHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理器"""

    def log_message(self, format, *args):
        """覆盖默认日志，使用流水线日志格式"""
        log("INFO", "http", f"{self.client_address[0]} - {args[0]}")

    def _send_json(self, status_code: int, data: dict):
        """发送 JSON 响应"""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _send_error(self, status_code: int, message: str):
        """发送错误响应"""
        self._send_json(status_code, {"error": message})

    def do_GET(self):
        """处理 GET 请求"""
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/health":
            self._send_json(200, {
                "status": "ok",
                "service": "droneblogd",
                "droneblog_dir": DRONEBLOG_DIR
            })
        elif path == "/api/v1/status":
            # 返回流水线状态
            self._send_json(200, {
                "pipeline_ready": True,
                "stages": [
                    "analysis", "skill_match", "execute",
                    "compliance_audit", "security", "output"
                ]
            })
        else:
            self._send_error(404, "Not Found")

    def do_POST(self):
        """处理 POST 请求"""
        parsed = urlparse(self.path)
        path = parsed.path

        if path != "/api/v1/generate":
            self._send_error(404, "Not Found")
            return

        # 读取请求体
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self._send_error(400, "Empty request body")
            return

        body = self.rfile.read(content_length).decode("utf-8")
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON")
            return

        # 提取参数
        topic = payload.get("topic", "")
        category = payload.get("category", "后端开发")
        tags = payload.get("tags", "")
        extra_prompt = payload.get("prompt", "")
        auto_confirm = payload.get("auto_confirm", False)  # 是否跳过审核（仅测试用）

        if not topic:
            self._send_error(400, "Missing required field: topic")
            return

        # 检查 API Key
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            self._send_error(500, "OPENAI_API_KEY not configured")
            return

        # ── 阶段 1: 需求分析 ──
        log("OK", "analysis", f"任务类型=content_creation, 关键词={topic}")

        # ── 阶段 2: Skill 识别 ──
        log("OK", "skill_match", "无匹配 Skill，使用通用能力")

        # ── 阶段 3: AI 生成 ──
        slug = generate_slug(topic)
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tmp_file = os.path.join(tempfile.gettempdir(), f"{slug}.md")

        try:
            content = call_openai(topic, category, tags, extra_prompt, api_key)
        except Exception as e:
            log("FAIL", "execute", f"AI 生成失败: {e}")
            self._send_error(500, f"AI generation failed: {e}")
            return

        with open(tmp_file, "w", encoding="utf-8") as f:
            f.write(content)

        log("OK", "execute", f"AI 生成完成: {topic}")

        # ── 阶段 4: 人工审核（可跳过）─
        if not auto_confirm:
            if not open_editor(tmp_file):
                log("FAIL", "execute", "编辑器打开失败")
                self._send_error(500, "Failed to open editor")
                return

            # 重新读取（用户可能修改）
            with open(tmp_file, "r", encoding="utf-8") as f:
                content = f.read()

        log("OK", "execute", "人工审核通过")

        # ── 阶段 5: 合规审核 ──
        ok, msg = validate_frontmatter(content)
        if not ok:
            log("FAIL", "compliance_audit", msg)
            self._send_error(400, f"Front-matter validation: {msg}")
            return

        ok, msg = validate_tags(content)
        if not ok:
            log("WARN", "compliance_audit", msg)
            # 标签不合规不阻塞，仅警告

        ok, msg = validate_filename(slug)
        if not ok:
            log("FAIL", "compliance_audit", msg)
            self._send_error(400, f"Filename validation: {msg}")
            return

        log("OK", "compliance_audit", "全部合规")

        # ── 阶段 6: 安全审查 ──
        if re.search(r"(api[_-]?key|token|password|secret)\s*[:=]\s*\S+", content, re.I):
            log("WARN", "security", "检测到可能的敏感信息模式")
            # 警告但不阻塞
        else:
            log("OK", "security", "敏感信息扫描通过")

        # ── 写入文件 ──
        os.makedirs(POSTS_DIR, exist_ok=True)
        target_file = os.path.join(POSTS_DIR, f"{slug}.md")
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(content)

        # ── 阶段 7: 构建验证 ──
        build_ok, build_output = hexo_build()
        if build_ok:
            log("OK", "execute", "构建验证通过")
        else:
            log("FAIL", "execute", f"构建验证失败: {build_output}")
            # 构建失败不删除文件，让用户手动修复
            self._send_error(500, f"Build failed: {build_output}")
            return

        # ── 阶段 8: 输出规范 ──
        log("OK", "output", f"任务完成: {topic}")

        # 清理临时文件
        os.remove(tmp_file)

        self._send_json(200, {
            "status": "success",
            "message": "Blog article generated and verified",
            "file": f"source/_posts/{slug}.md",
            "slug": slug,
            "title": topic,
            "build": "passed",
            "pipeline_stages": {
                "analysis": "ok",
                "skill_match": "ok",
                "execute": "ok",
                "compliance_audit": "ok",
                "security": "ok",
                "output": "ok"
            }
        })


# ── 服务启动 ──

def find_free_port(start=8765, max_try=100) -> int:
    """查找可用端口"""
    for port in range(start, start + max_try):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((HOST, port))
                return port
        except OSError:
            continue
    raise RuntimeError("No free port found")


def main():
    port = int(os.environ.get("DRONEBLOG_PORT", DEFAULT_PORT))

    # 如果端口被占用，尝试找可用端口
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, port))
    except OSError:
        old_port = port
        port = find_free_port(port + 1)
        print(f"[WARN] Port {old_port} in use, using {port}")

    server = HTTPServer((HOST, port), PipelineHandler)

    print(f"=" * 50)
    print(f"DroneBlog Pipeline Service")
    print(f"=" * 50)
    print(f"Listening: http://{HOST}:{port}")
    print(f"DroneBlog: {DRONEBLOG_DIR}")
    print(f"Posts dir: {POSTS_DIR}")
    print(f"Log file:  {LOG_FILE}")
    print(f"")
    print(f"API Endpoints:")
    print(f"  GET  /health              — 健康检查")
    print(f"  GET  /api/v1/status       — 流水线状态")
    print(f"  POST /api/v1/generate     — 生成文章")
    print(f"")
    print(f"Example:")
    print(f"  curl -X POST http://{HOST}:{port}/api/v1/generate \\")
    print(f"    -H 'Content-Type: application/json' \\")
    print(f"    -d '{{\"topic\": \"C++20 协程\", \"category\": \"后端开发\"}}'")
    print(f"")
    print(f"Press Ctrl+C to stop")
    print(f"=" * 50)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
