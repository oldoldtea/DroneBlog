"""核心工具函数单元测试：slug/校验/front-matter/字数/敏感信息。"""

import pytest

from droneblog_mcp.utils.fs import (
    build_frontmatter,
    count_words,
    generate_slug,
    parse_frontmatter,
    scan_sensitive_info,
    validate_filename,
    validate_frontmatter,
    validate_tags,
)


@pytest.mark.parametrize(
    "title,expected",
    [
        ("C++ Core Features", "c-core-features"),
        ("React Hooks Deep Dive", "react-hooks-deep-dive"),
        ("Kafka 消息传输", "kafka"),  # 混合标题仅保留 ASCII 部分
        ("hello--world  again", "hello-world-again"),
    ],
)
def test_generate_slug_ascii(title, expected):
    assert generate_slug(title) == expected


def test_generate_slug_pure_cjk_is_empty():
    """纯中文标题派生出空 slug——调用方必须据此要求显式 slug。"""
    assert generate_slug("消息传输机制源码解析") == ""


@pytest.mark.parametrize(
    "slug,ok",
    [
        ("cpp-core-features", True),
        ("react-hooks", True),
        ("", False),  # 空 slug 拒绝
        ("C++语言", False),
        ("react_hooks", False),
        ("with space", False),
        ("CamelCase", False),
    ],
)
def test_validate_filename(slug, ok):
    assert validate_filename(slug)[0] is ok


def test_validate_frontmatter_ok():
    content = "---\ntitle: 测试\ndate: 2026-07-11 10:00:00\n---\n\n正文"
    ok, msg = validate_frontmatter(content)
    assert ok is True
    assert msg == ""


def test_validate_frontmatter_missing_header():
    ok, _ = validate_frontmatter("# 没有 front-matter")
    assert ok is False


def test_validate_frontmatter_missing_title():
    ok, _ = validate_frontmatter("---\ndate: 2026-07-11\n---\n")
    assert ok is False


def test_validate_tags_boundaries():
    base = "---\ntitle: t\ntags:\n{items}\n---\n"

    def with_tags(n):
        return base.format(items="\n".join("  - C++" for _ in range(n)))

    assert validate_tags(with_tags(2))[0] is True
    assert validate_tags(with_tags(3))[0] is True
    assert validate_tags(with_tags(1))[0] is False
    assert validate_tags(with_tags(4))[0] is False


def test_frontmatter_roundtrip():
    metadata = {"title": "测试", "tags": ["C++", "并发"], "categories": ["系统编程"]}
    body = "这是正文。"
    content = build_frontmatter(metadata, body)
    parsed_meta, parsed_body = parse_frontmatter(content)
    assert parsed_meta["title"] == "测试"
    assert parsed_meta["tags"] == ["C++", "并发"]
    assert parsed_body == body


def test_count_words_mixed():
    # 2 个中文字 + 1 个英文单词 = 3
    assert count_words("Hello 世界") == 3


def test_scan_sensitive_info():
    content = "api_key = sk-abc12345678901234567890\npassword: hunter2"
    findings = scan_sensitive_info(content)
    assert len(findings) >= 2
    assert scan_sensitive_info("普通文本，没有密钥") == []
