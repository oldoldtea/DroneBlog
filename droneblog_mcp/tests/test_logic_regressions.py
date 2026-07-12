"""逻辑缺陷回归测试（2026-07 全接口测试发现并修复）。

覆盖：
- F1/F8: ``list_posts`` 按日期倒序（曾按文件名倒序）；年份筛选容忍多种日期格式
- F7: ``read_post`` 的 date/updated 统一为字符串（yaml 会解析出 datetime 对象）
- F2: ``set_site_config`` 对标量中间节点深入时返回清晰失败而非 TypeError 崩溃
- F3: ``theme_config_file`` 动态解析（themes/<name> > node_modules/hexo-theme-<name>），
      不再硬编码 hexo-theme-maple
"""

import pytest

from droneblog_mcp.models.config import DroneBlogConfig, get_config, set_config
from droneblog_mcp.utils.fs import extract_markdown, list_posts, read_post, write_post
from droneblog_mcp.utils.yaml import get_site_config, set_site_config

POST_TMPL = """---
title: {title}
date: {date}
tags:
  - A
  - B
categories:
  - 后端开发
---

正文内容
"""


@pytest.fixture
def tmp_blog(tmp_path):
    """临时博客目录：切换全局配置指向它，测试后还原。"""
    (tmp_path / "source" / "_posts").mkdir(parents=True)
    (tmp_path / "_config.yml").write_text("title: TmpBlog\ntheme: landscape\n", encoding="utf-8")
    prev = get_config()
    set_config(DroneBlogConfig(dir=tmp_path))
    yield tmp_path
    set_config(prev)


def _write(blog, slug, title, date):
    write_post(slug, POST_TMPL.format(title=title, date=date))


def test_list_posts_sorted_by_date_desc(tmp_blog):
    # 文件名顺序与日期顺序故意相反
    _write(tmp_blog, "aaa-first", "A", "2020-01-01 10:00:00")
    _write(tmp_blog, "mmm-middle", "M", "2026-01-01 10:00:00")
    _write(tmp_blog, "zzz-last", "Z", "2023-06-15 10:00:00")

    posts = list_posts()
    assert [p["slug"] for p in posts] == ["mmm-middle", "zzz-last", "aaa-first"], (
        f"应按日期倒序: {[p['slug'] for p in posts]}"
    )


def test_list_posts_year_filter_tolerant_of_date_formats(tmp_blog):
    _write(tmp_blog, "iso-date", "ISO", "2025-03-01T10:00:00")  # ISO 格式
    _write(tmp_blog, "normal-date", "Normal", "2025-04-01 10:00:00")
    _write(tmp_blog, "other-year", "Other", "2024-04-01 10:00:00")

    posts = list_posts(year=2025)
    slugs = {p["slug"] for p in posts}
    assert slugs == {"iso-date", "normal-date"}, f"年份筛选应容忍 ISO 格式: {slugs}"


def test_read_post_date_fields_are_strings(tmp_blog):
    _write(tmp_blog, "some-post", "T", "2025-05-06 07:08:09")
    post = read_post("some-post")
    assert post is not None
    assert isinstance(post["date"], str), f"date 应为字符串: {type(post['date'])}"
    assert post["date"] == "2025-05-06 07:08:09"


def test_set_site_config_nested_into_scalar_fails_cleanly(tmp_blog):
    # title 是标量，对 title.en 深入应返回清晰失败而非 TypeError 崩溃
    ok, msg = set_site_config("site", "title.en", "x")
    assert ok is False, "对标量中间节点深入应失败"
    assert "title" in msg and "不是映射" in msg, f"错误信息应定位中间节点: {msg}"


def test_set_site_config_creates_missing_intermediate(tmp_blog):
    ok, msg = set_site_config("site", "deploy.branch", "master")
    assert ok, msg
    cfg = get_site_config("site")
    assert cfg["deploy"]["branch"] == "master"


def test_theme_config_file_prefers_local_themes_dir(tmp_blog):
    # themes/<name> 优先于 node_modules
    local = tmp_blog / "themes" / "landscape" / "_config.yml"
    local.parent.mkdir(parents=True)
    local.write_text("menu: {home: /}\n", encoding="utf-8")
    npm = tmp_blog / "node_modules" / "hexo-theme-landscape" / "_config.yml"
    npm.parent.mkdir(parents=True)
    npm.write_text("menu: {home: /}\n", encoding="utf-8")

    cfg = get_config()
    assert cfg.theme_name == "landscape"
    assert cfg.theme_config_file == local


def test_theme_config_file_falls_back_to_node_modules(tmp_blog):
    npm = tmp_blog / "node_modules" / "hexo-theme-landscape" / "_config.yml"
    npm.parent.mkdir(parents=True)
    npm.write_text("menu: {home: /}\n", encoding="utf-8")

    cfg = get_config()
    assert cfg.theme_config_file == npm


def test_theme_config_file_not_hardcoded(tmp_blog):
    # 无任何主题文件时返回首选路径（themes/landscape），而非旧版的 hexo-theme-maple
    cfg = get_config()
    assert "hexo-theme-maple" not in str(cfg.theme_config_file)
    assert cfg.theme_config_file == tmp_blog / "themes" / "landscape" / "_config.yml"


# === F9: extract_markdown 清洗模型输出（剥代码栅栏 / 去前导语）===

ARTICLE = """---
title: 测试文章
date: 2026-07-12
tags:
  - Python
  - MCP
categories:
  - 后端开发
---

# 正文

内容。
"""


def test_extract_markdown_plain_passthrough():
    # 本就干净的输出原样返回
    assert extract_markdown(ARTICLE) == ARTICLE.strip()


def test_extract_markdown_strips_code_fence():
    wrapped = f"```markdown\n{ARTICLE}```\n"
    assert extract_markdown(wrapped) == ARTICLE.strip()


def test_extract_markdown_strips_four_backtick_fence_with_inner_code_block():
    # 真实 Kimi 情形：外层 4 反引号包裹，正文内含 3 反引号代码块
    body = ARTICLE + "\n```cpp\nint main(){}\n```\n"
    wrapped = f"````markdown\n{body}````\n"
    out = extract_markdown(wrapped)
    assert out.startswith("---")
    assert "title: 测试文章" in out
    assert "```cpp" in out  # 内层代码块保留
    assert not out.rstrip().endswith("````")


def test_extract_markdown_three_backtick_wrapper_does_not_truncate_inner_code():
    # 外层 3 反引号 + 正文含 3 反引号代码块：不得在内层闭合处提前截断（曾因此丢正文）
    body = ARTICLE + "\n```python\nprint('hi')\n```\n\n结尾段。\n"
    wrapped = f"```markdown\n{body}```\n"
    out = extract_markdown(wrapped)
    assert out.startswith("---")
    assert "```python" in out
    assert "print('hi')" in out
    assert "结尾段。" in out  # 正文未被截断
    assert not out.rstrip().endswith("```")


def test_extract_markdown_keeps_body_ending_code_block():
    # 正文自身以代码块结尾 + 外层栅栏：只去外层配对栅栏，保留代码块闭合
    body = ARTICLE + "\n```python\nprint('hi')\n```\n"
    wrapped = f"```markdown\n{body}```\n"
    out = extract_markdown(wrapped)
    # 去掉外层配对栅栏后，正文的代码块闭合 ``` 应保留
    assert out.rstrip().endswith("```")
    assert out.count("```python") == 1


def test_extract_markdown_drops_preamble_and_stray_separator():
    # 前导语 + 孤立 --- 分隔线 + 栅栏包裹（Kimi 实测输出形态）
    noisy = f"好的，以下是文章：\n\n---\n\n```markdown\n{ARTICLE}```\n"
    out = extract_markdown(noisy)
    assert out.startswith("---")
    assert "title: 测试文章" in out
    assert "好的" not in out


def test_extract_markdown_no_frontmatter_returns_as_is():
    # 找不到合法 frontmatter 时原样返回，交由 validate_frontmatter 报错
    bad = "没有 frontmatter 的输出"
    assert extract_markdown(bad) == bad


# === F10: hexo_build 不得因 npx 交互安装/读 stdin 挂死 ===


def test_resolve_hexo_npx_fallback_uses_no_install(tmp_path, monkeypatch):
    # 模拟：无本地 node_modules/.bin/hexo、无全局 hexo，仅有 npx
    from droneblog_mcp.utils import fs

    monkeypatch.setattr(fs.shutil, "which", lambda name: "/usr/bin/npx" if name == "npx" else None)
    prefix = fs._resolve_hexo(tmp_path)
    assert prefix is not None and prefix[0].endswith("npx")
    assert "--no-install" in prefix, "npx 回退必须带 --no-install，避免交互安装挂死"


def test_run_hexo_detaches_stdin(tmp_path, monkeypatch):
    # _run_hexo 必须以 stdin=DEVNULL 调用子进程，杜绝任何交互提示阻塞
    from droneblog_mcp.utils import fs

    captured = {}

    class _FakeProc:
        returncode = 0
        stdout = "ok"
        stderr = ""

    def fake_run(cmd, **kwargs):
        captured.update(kwargs)
        return _FakeProc()

    monkeypatch.setattr(fs, "_resolve_hexo", lambda d: ["/bin/echo"])
    monkeypatch.setattr(fs.subprocess, "run", fake_run)
    fs._run_hexo(tmp_path, ["generate"])
    assert captured.get("stdin") is fs.subprocess.DEVNULL, "hexo 子进程必须断开 stdin"

