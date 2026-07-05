"""DroneBlog MCP Server - AI Content Generator"""

import json
import os
from typing import Optional

from droneblog_mcp.models.config import get_config
from droneblog_mcp.utils.log import log


def call_openai(
    topic: str,
    category: str,
    tags: list[str],
    extra_prompt: str = "",
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> str:
    """调用 OpenAI API 生成文章"""
    config = get_config()
    api_key = config.openai_api_key or os.environ.get("OPENAI_API_KEY", "")

    if not api_key:
        raise ValueError("OPENAI_API_KEY not configured")

    model = model or config.model
    temperature = temperature or config.temperature
    max_tokens = max_tokens or config.max_tokens

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

    tags_str = ", ".join(tags) if tags else ""
    user_prompt = f"""请写一篇技术博客。

主题: {topic}
分类: {category}
{f"标签要求: {tags_str}" if tags_str else ""}
{f"额外要求: {extra_prompt}" if extra_prompt else ""}

请输出完整的 Markdown 文件内容，包含 YAML Front-matter。"""

    import urllib.request
    import urllib.error

    data = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise RuntimeError(f"OpenAI API error: {e.code} - {error_body}")
    except Exception as e:
        raise RuntimeError(f"OpenAI request failed: {e}")


def generate_article(
    topic: str,
    category: str,
    tags: list[str],
    prompt: str = "",
    model: Optional[str] = None,
) -> dict:
    """生成文章并返回结果"""
    config = get_config()

    # 阶段 1: 需求分析
    log("OK", "analysis", f"任务类型=content_creation, 关键词={topic}")

    # 阶段 2: Skill 识别
    log("OK", "skill_match", "无匹配 Skill，使用通用能力")

    # 阶段 3: AI 生成
    try:
        content = call_openai(topic, category, tags, prompt, model)
        log("OK", "execute", f"AI 生成完成: {topic}")
    except Exception as e:
        log("FAIL", "execute", f"AI 生成失败: {e}")
        raise

    return {"content": content, "topic": topic, "category": category, "tags": tags}
