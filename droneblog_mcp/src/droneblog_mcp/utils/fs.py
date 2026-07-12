"""DroneBlog MCP Server - File System Utilities"""

import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml

from droneblog_mcp.models.config import get_config

# hexo 子进程默认超时（秒）。构建/部署偶尔较慢，给足上限但绝不无限挂起。
HEXO_TIMEOUT = 300


def ensure_dir(path: Path) -> None:
    """确保目录存在"""
    path.mkdir(parents=True, exist_ok=True)


def generate_slug(title: str) -> str:
    """从标题生成 kebab-case slug。

    仅保留 ASCII 小写字母/数字，其余字符折叠为短横线。
    注意：纯中文/非 ASCII 标题会得到空字符串——调用方必须处理空 slug
    （见 ``blog_generate`` 的显式 ``slug`` 参数与 ``write_post`` 守卫）。
    """
    slug = re.sub(r"[^a-z0-9]", "-", title.lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


def validate_frontmatter(content: str) -> tuple[bool, str]:
    """校验 Front-matter 格式"""
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return False, "缺少 YAML Front-matter（应以 --- 开头）"
    if not re.search(r"^title:\s*\S+", content, re.MULTILINE):
        return False, "Front-matter 中缺少 title 字段"
    return True, ""


def extract_markdown(content: str) -> str:
    """从模型输出中提取真正的 Markdown（frontmatter + 正文）。

    大模型常把整篇包在代码栅栏里（```` ```markdown ````，正文含三反引号代码块时外层
    常用四反引号），或在 frontmatter 前加前导语（"好的，以下是文章…"）甚至一条孤立的
    ``---`` 分隔线。直接拿原始输出校验 frontmatter 会误报。

    策略（不解栅栏，避免非贪婪正则在内层代码块处提前截断）：

    1. 定位**真正**的 frontmatter——第一对 ``---`` 之间含 ``title:`` 字段。
       其前的前导语、孤立 ``---``、外层栅栏起始行都被自然跳过；
    2. 仅当 frontmatter 之前确实存在外层栅栏起始行时，去掉文末**一根**栅栏线
       （与开头配对），不误伤正文结尾自身的代码块。

    找不到合法 frontmatter 时原样返回，交由 ``validate_frontmatter`` 报清晰错误。
    """
    text = content.strip()
    if not text:
        return text
    lines = text.split("\n")
    n = len(lines)

    # 1) 定位 frontmatter：第一对 --- 之间含 title:
    start = None
    for i in range(n):
        if lines[i].strip() != "---":
            continue
        for j in range(i + 1, n):
            if lines[j].strip() == "---":
                block = "\n".join(lines[i + 1 : j])
                if re.search(r"^title:\s*\S+", block, re.MULTILINE):
                    start = i
                break
        if start is not None:
            break

    if start is None:
        return text  # 无合法 frontmatter，原样返回

    kept = lines[start:]

    # 2) frontmatter 之前有外层栅栏起始 → 去掉文末一根与之配对的栅栏线
    opening_before = any(re.match(r"^\s*`{3,}", ln) for ln in lines[:start])
    if opening_before:
        while kept and not kept[-1].strip():
            kept.pop()
        if kept and re.fullmatch(r"`{3,}", kept[-1].strip()):
            kept.pop()

    return "\n".join(kept).strip()


def validate_tags(content: str, min_tags: int = 2, max_tags: int = 3) -> tuple[bool, str]:
    """校验标签数量"""
    tags = re.findall(r"^  - (.+)$", content, re.MULTILINE)
    if len(tags) < min_tags or len(tags) > max_tags:
        return False, f"标签数量 {len(tags)} 个，应为 {min_tags}-{max_tags} 个"
    return True, ""


def validate_filename(slug: str) -> tuple[bool, str]:
    """校验文件名规范（非空、仅含小写字母/数字/短横线）"""
    if not slug:
        return False, "文件名不能为空（请提供 kebab-case 的 slug）"
    if not re.match(r"^[a-z0-9-]+$", slug):
        return False, "文件名应仅包含小写字母、数字和短横线"
    return True, ""


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """解析 YAML Front-matter，返回 (metadata, body)"""
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    try:
        metadata = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        metadata = {}

    body = parts[2].strip()
    return metadata, body


def build_frontmatter(metadata: dict, body: str) -> str:
    """构建带 Front-matter 的 Markdown 内容"""
    frontmatter = yaml.dump(metadata, allow_unicode=True, sort_keys=False)
    return f"---\n{frontmatter}---\n\n{body}"


def scan_sensitive_info(content: str) -> list[str]:
    """扫描敏感信息"""
    patterns = [
        r"(api[_-]?key|token|password|secret|private[_-]?key)\s*[:=]\s*\S+",
        r"sk-[a-zA-Z0-9]{20,}",
        r"ghp_[a-zA-Z0-9]{36}",
        r"github_pat_[a-zA-Z0-9_]{20,}",
    ]
    findings = []
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            findings.append(match.group())
    return findings


def count_words(text: str) -> int:
    """统计字数（支持中英文混合）"""
    # 中文字符
    chinese_chars = len(re.findall(r"[一-鿿]", text))
    # 英文单词
    english_words = len(re.findall(r"[a-zA-Z]+", text))
    return chinese_chars + english_words


# 支持的 front-matter 日期格式（按项目中出现频率排序）
_DATE_FORMATS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d")


def _parse_post_date(value) -> datetime | None:
    """容忍多种格式的日期解析；失败返回 None（调用方决定兜底策略）。"""
    if isinstance(value, datetime):
        return value
    if value is None:
        return None
    text = str(value).strip()
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def list_posts(
    category: str | None = None,
    tag: str | None = None,
    year: int | None = None,
    limit: int = 20,
) -> list[dict]:
    """列出博客文章，按发布日期**倒序**（最新在前）。

    排序依据 front-matter 的 ``date``（解析失败的文章排末尾、按文件名兜底），
    而非文件名——文件名顺序与发布时间无任何关系。
    """
    config = get_config()
    posts_dir = config.posts_dir

    if not posts_dir.exists():
        return []

    entries = []
    for md_file in posts_dir.glob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            metadata, body = parse_frontmatter(content)

            post_date = metadata.get("date", "")
            parsed = _parse_post_date(post_date)
            if year:
                if parsed is not None:
                    if parsed.year != year:
                        continue
                elif not str(post_date).startswith(str(year)):
                    # 日期不可解析时退化为字符串前缀匹配，避免静默丢文章
                    continue

            post_tags = metadata.get("tags", []) or []
            if tag and tag not in post_tags:
                continue

            post_categories = metadata.get("categories", []) or []
            if category and category not in post_categories:
                continue

            entries.append(
                (
                    parsed or datetime.min,
                    md_file.stem,
                    {
                        "slug": md_file.stem,
                        "title": metadata.get("title", md_file.stem),
                        "date": str(post_date),
                        "tags": post_tags,
                        "categories": post_categories,
                        "word_count": count_words(body),
                    },
                )
            )
        except Exception:
            continue

    # 日期倒序；同日按文件名倒序兜底，保证确定性
    entries.sort(key=lambda e: (e[0], e[1]), reverse=True)
    return [e[2] for e in entries[:limit]]


def read_post(slug: str) -> dict | None:
    """读取单篇博客文章"""
    config = get_config()
    posts_dir = config.posts_dir
    md_file = posts_dir / f"{slug}.md"

    if not md_file.exists():
        return None

    content = md_file.read_text(encoding="utf-8")
    metadata, body = parse_frontmatter(content)

    # date/updated 经 yaml 解析后可能是 datetime 对象，统一转字符串，
    # 与 list_posts 的输出类型保持一致（"YYYY-MM-DD HH:MM:SS"）
    updated = metadata.get("updated")
    return {
        "slug": slug,
        "title": metadata.get("title", slug),
        "date": str(metadata.get("date", "") or ""),
        "updated": str(updated) if updated else None,
        "tags": metadata.get("tags", []) or [],
        "categories": metadata.get("categories", []) or [],
        "content": body,
        "raw_content": content,
        "word_count": count_words(body),
    }


def write_post(slug: str, content: str) -> Path:
    """写入博客文章。空/非法 slug 直接抛错，避免写出 ``source/_posts/.md``。"""
    ok, msg = validate_filename(slug)
    if not ok:
        raise ValueError(f"非法 slug，拒绝写入: {msg}")

    config = get_config()
    posts_dir = config.posts_dir
    ensure_dir(posts_dir)

    file_path = posts_dir / f"{slug}.md"
    file_path.write_text(content, encoding="utf-8")
    return file_path


def delete_post(slug: str) -> bool:
    """删除博客文章"""
    config = get_config()
    posts_dir = config.posts_dir
    md_file = posts_dir / f"{slug}.md"

    if md_file.exists():
        md_file.unlink()
        return True
    return False


def _resolve_hexo(blog_dir: Path) -> list[str] | None:
    """解析调用 hexo 的 argv 前缀，找不到则返回 None。

    优先级：项目本地 ``node_modules/.bin/hexo`` > 全局 ``hexo`` > ``npx hexo``。
    使用 ``shutil.which`` 在 Windows 上也能正确解析 ``.cmd`` 启动器。
    """
    bin_dir = blog_dir / "node_modules" / ".bin"
    candidates = []
    if sys.platform == "win32":
        candidates.append(bin_dir / "hexo.cmd")
    candidates.append(bin_dir / "hexo")
    for cand in candidates:
        if cand.exists():
            return [str(cand)]

    hexo = shutil.which("hexo")
    if hexo:
        return [hexo]

    npx = shutil.which("npx")
    if npx:
        # --no-install：本地没有 hexo 时立即报错，绝不触发交互式安装提示（会读 stdin 挂死）
        return [npx, "--no-install", "hexo"]
    return None


def _run_hexo(blog_dir: Path, args: list[str], timeout: int = HEXO_TIMEOUT) -> tuple[bool, str]:
    """在 ``blog_dir`` 下以子进程执行 hexo，捕获输出，带超时。无 shell、无注入。

    ``stdin=DEVNULL``：任何交互提示（npx 安装确认、deploy 的登录询问等）立即吃 EOF，
    绝不阻塞等待输入——MCP 子进程没有可交互的 TTY。
    """
    prefix = _resolve_hexo(blog_dir)
    if prefix is None:
        return False, "未找到 hexo：请在博客目录执行 `npm install`，或全局安装 `hexo-cli`"

    cmd = prefix + args
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(blog_dir),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        return False, f"`{' '.join(cmd)}` 执行超时（>{timeout}s）"
    except OSError as e:
        return False, f"执行 hexo 失败: {e}"

    output = ((proc.stdout or "") + (proc.stderr or "")).strip()

    # hexo CLI 在未识别为有效站点（目录缺 package.json/本地 hexo）时，对 clean/generate/
    # deploy 等子命令只打印帮助信息且**退出码为 0**——不能把"打印帮助"误判为执行成功，
    # 否则用户没 npm install 时 hexo_build 会谎报 Build successful。
    if "Get help on a command" in output:
        head = "\n".join(output.splitlines()[:8])
        return False, (
            "hexo 未真正执行命令（输出了 CLI 帮助而非构建）：当前目录可能不是有效的 hexo "
            "站点，或缺少 node_modules（请先在博客目录执行 npm install）。原始输出:\n" + head
        )

    if proc.returncode != 0:
        # 失败时回传真实输出（截断尾部），便于 debug_build 定位
        tail = "\n".join(output.splitlines()[-40:]) if output else ""
        return False, tail or f"hexo 退出码 {proc.returncode}"

    tail = "\n".join(output.splitlines()[-15:]) if output else ""
    return True, ("Build successful" + (f"\n{tail}" if tail else ""))


def hexo_build(clean: bool = True) -> tuple[bool, str]:
    """执行构建验证（subprocess，捕获输出，带超时）。

    Args:
        clean: 为 True 时先执行 ``hexo clean``，否则仅 ``hexo generate``。
    """
    config = get_config()
    blog_dir = config.dir

    if clean:
        ok, msg = _run_hexo(blog_dir, ["clean"])
        if not ok:
            return False, f"hexo clean 失败:\n{msg}"

    ok, msg = _run_hexo(blog_dir, ["generate"])
    if not ok:
        return False, f"hexo generate 失败:\n{msg}"

    return True, msg or "Build successful"


def hexo_deploy() -> tuple[bool, str]:
    """执行 ``hexo deploy`` 部署（subprocess，捕获输出，带超时）。"""
    config = get_config()
    blog_dir = config.dir

    ok, msg = _run_hexo(blog_dir, ["deploy"])
    if not ok:
        return False, f"hexo deploy 失败:\n{msg}"
    return True, msg or "Deploy successful"
