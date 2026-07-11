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
from droneblog_mcp.utils.fs import list_posts, read_post, write_post
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
