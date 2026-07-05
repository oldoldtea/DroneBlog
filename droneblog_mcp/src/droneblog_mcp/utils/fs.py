"""DroneBlog MCP Server - File System Utilities"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import yaml

from droneblog_mcp.models.config import get_config


def ensure_dir(path: Path) -> None:
    """确保目录存在"""
    path.mkdir(parents=True, exist_ok=True)


def generate_slug(title: str) -> str:
    """生成 kebab-case slug"""
    slug = re.sub(r"[^a-z0-9]", "-", title.lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


def validate_frontmatter(content: str) -> Tuple[bool, str]:
    """校验 Front-matter 格式"""
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return False, "缺少 YAML Front-matter（应以 --- 开头）"
    if not re.search(r"^title:\s*\S+", content, re.MULTILINE):
        return False, "Front-matter 中缺少 title 字段"
    return True, ""


def validate_tags(content: str, min_tags: int = 2, max_tags: int = 3) -> Tuple[bool, str]:
    """校验标签数量"""
    tags = re.findall(r"^  - (.+)$", content, re.MULTILINE)
    if len(tags) < min_tags or len(tags) > max_tags:
        return False, f"标签数量 {len(tags)} 个，应为 {min_tags}-{max_tags} 个"
    return True, ""


def validate_filename(slug: str) -> Tuple[bool, str]:
    """校验文件名规范"""
    if not re.match(r"^[a-z0-9-]+$", slug):
        return False, "文件名应仅包含小写字母、数字和短横线"
    return True, ""


def parse_frontmatter(content: str) -> Tuple[dict, str]:
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


def scan_sensitive_info(content: str) -> List[str]:
    """扫描敏感信息"""
    patterns = [
        r"(api[_-]?key|token|password|secret|private[_-]?key)\s*[:=]\s*\S+",
        r"sk-[a-zA-Z0-9]{20,}",
        r"ghp_[a-zA-Z0-9]{36}",
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
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    # 英文单词
    english_words = len(re.findall(r"[a-zA-Z]+", text))
    return chinese_chars + english_words


def list_posts(
    category: Optional[str] = None,
    tag: Optional[str] = None,
    year: Optional[int] = None,
    limit: int = 20,
) -> List[dict]:
    """列出博客文章"""
    config = get_config()
    posts_dir = config.posts_dir

    if not posts_dir.exists():
        return []

    posts = []
    for md_file in sorted(posts_dir.glob("*.md"), reverse=True):
        try:
            content = md_file.read_text(encoding="utf-8")
            metadata, body = parse_frontmatter(content)

            post_date = metadata.get("date", "")
            if year and post_date:
                try:
                    post_year = datetime.strptime(str(post_date), "%Y-%m-%d %H:%M:%S").year
                    if post_year != year:
                        continue
                except ValueError:
                    continue

            post_tags = metadata.get("tags", []) or []
            if tag and tag not in post_tags:
                continue

            post_categories = metadata.get("categories", []) or []
            if category and category not in post_categories:
                continue

            posts.append({
                "slug": md_file.stem,
                "title": metadata.get("title", md_file.stem),
                "date": str(post_date),
                "tags": post_tags,
                "categories": post_categories,
                "word_count": count_words(body),
            })
        except Exception:
            continue

    return posts[:limit]


def read_post(slug: str) -> Optional[dict]:
    """读取单篇博客文章"""
    config = get_config()
    posts_dir = config.posts_dir
    md_file = posts_dir / f"{slug}.md"

    if not md_file.exists():
        return None

    content = md_file.read_text(encoding="utf-8")
    metadata, body = parse_frontmatter(content)

    return {
        "slug": slug,
        "title": metadata.get("title", slug),
        "date": metadata.get("date", ""),
        "updated": metadata.get("updated", None),
        "tags": metadata.get("tags", []) or [],
        "categories": metadata.get("categories", []) or [],
        "content": body,
        "raw_content": content,
        "word_count": count_words(body),
    }


def write_post(slug: str, content: str) -> Path:
    """写入博客文章"""
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


def hexo_build() -> Tuple[bool, str]:
    """执行 hexo clean && hexo generate 构建验证"""
    config = get_config()
    blog_dir = config.dir

    try:
        # hexo clean
        result_clean = os.system(f"cd {blog_dir} && npx hexo clean > /dev/null 2>&1")
        if result_clean != 0:
            return False, "hexo clean failed"

        # hexo generate
        result_generate = os.system(f"cd {blog_dir} && npx hexo generate > /dev/null 2>&1")
        if result_generate != 0:
            return False, "hexo generate failed"

        return True, "Build successful"
    except Exception as e:
        return False, str(e)


def hexo_deploy() -> Tuple[bool, str]:
    """执行 hexo deploy 部署"""
    config = get_config()
    blog_dir = config.dir

    try:
        result = os.system(f"cd {blog_dir} && npx hexo deploy > /dev/null 2>&1")
        if result != 0:
            return False, "hexo deploy failed"
        return True, "Deploy successful"
    except Exception as e:
        return False, str(e)
