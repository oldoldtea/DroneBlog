"""DroneBlog MCP Server - Pipeline Executor"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

from droneblog_mcp.core.generator import generate_article
from droneblog_mcp.models.config import get_config
from droneblog_mcp.utils.fs import (
    generate_slug,
    hexo_build,
    scan_sensitive_info,
    validate_filename,
    validate_frontmatter,
    validate_tags,
    write_post,
)
from droneblog_mcp.utils.log import log


def _resolve_slug(topic: str, slug: str) -> tuple[str | None, str | None]:
    """确定最终 slug。返回 ``(slug, error)``；``error`` 非空表示不可用。

    优先使用调用方显式提供的 ``slug``；否则从 ``topic`` 派生。纯中文标题会派生出
    空 slug，此时返回清晰错误，要求显式传 ``slug``，绝不写出 ``source/_posts/.md``。
    """
    candidate = (slug or "").strip().lower() or generate_slug(topic)
    ok, msg = validate_filename(candidate)
    if not ok:
        return None, (
            f"无法从标题生成合法 slug（候选 {candidate!r}：{msg}）。"
            "请在调用 blog_generate 时显式提供 kebab-case 的 slug 参数"
            "（仅含小写字母/数字/短横线）。"
        )
    return candidate, None


def _maybe_review_in_editor(content: str, slug: str) -> tuple[str, bool]:
    """仅在显式 ``interactive=True`` 且存在 TTY 时打开 ``$EDITOR``。

    MCP/无 TTY 场景直接跳过，绝不阻塞。返回 ``(可能被更新的 content, 是否打开了编辑器)``。
    """
    if not sys.stdin.isatty():
        return content, False
    tmp_file = Path(tempfile.gettempdir()) / f"{slug or 'draft'}.md"
    try:
        tmp_file.write_text(content, encoding="utf-8")
        editor = os.environ.get("EDITOR", "nano")
        subprocess.run([editor, str(tmp_file)], check=True)
        return tmp_file.read_text(encoding="utf-8"), True
    except Exception:
        # 编辑器不可用或用户取消：保持原内容，不阻断流水线
        return content, False
    finally:
        if tmp_file.exists():
            try:
                tmp_file.unlink()
            except OSError:
                pass


def run_pipeline(
    topic: str,
    category: str,
    tags: list[str],
    prompt: str = "",
    model: str | None = None,
    slug: str = "",
    auto_confirm: bool = True,
    auto_deploy: bool = False,
    interactive: bool = False,
) -> dict:
    """执行完整的 6 阶段 AI 流水线。

    阶段:
    1. 需求分析 (analysis)
    2. Skill 识别 (skill_match)
    3. 执行流程 - AI 生成 (execute)
    4. 流程合规审核 (compliance_audit)
    5. 安全审查 (security)
    6. 输出规范 (output)

    关键设计（适配 MCP stdio）：
    - 默认 ``auto_confirm=True``，**不**打开本地 ``$EDITOR``（无 TTY 会卡死/崩溃）；
      生成的草稿通过返回值的 ``draft`` 字段交还给调用方，由客户端在对话中审阅/改写。
    - 仅当 ``interactive=True`` 且检测到 TTY 时才进入本地编辑器审核（CLI 场景）。
    - 显式 ``slug`` 优先；纯中文标题必须显式传 ``slug``，否则返回清晰错误。
    """
    config = get_config()

    final_slug, slug_err = _resolve_slug(topic, slug)
    pipeline_result = {
        "status": "success",
        "message": "",
        "file": "",
        "slug": final_slug or "",
        "title": topic,
        "build_status": "pending",
        "pipeline_stages": {},
    }
    if slug_err:
        pipeline_result["status"] = "fail"
        pipeline_result["message"] = slug_err
        log("FAIL", "compliance_audit", slug_err)
        return pipeline_result

    try:
        # === 阶段 1-3: 需求分析 → Skill 识别 → AI 生成 ===
        result = generate_article(topic, category, tags, prompt, model)
        content = result["content"]
        for stage in ("analysis", "skill_match", "execute"):
            pipeline_result["pipeline_stages"][stage] = "ok"

        # === 阶段 4: 审核（默认对话内审阅，不阻塞）===
        if not auto_confirm and interactive:
            content, opened = _maybe_review_in_editor(content, final_slug)
            log("OK", "execute", "人工审核完成" if opened else "无 TTY，已跳过本地编辑器审核")
        else:
            log("OK", "execute", "跳过本地编辑器审核（草稿交还客户端，在对话中审阅）")

        # === 阶段 5: 合规审核 ===
        ok, msg = validate_frontmatter(content)
        if not ok:
            log("FAIL", "compliance_audit", msg)
            raise ValueError(f"Front-matter validation: {msg}")

        ok, msg = validate_tags(content, config.min_tags, config.max_tags)
        if not ok:
            log("WARN", "compliance_audit", msg)  # 标签不合规仅警告，不阻塞
        else:
            log("OK", "compliance_audit", "标签数量合规")

        log("OK", "compliance_audit", "全部合规")
        pipeline_result["pipeline_stages"]["compliance_audit"] = "ok"

        # === 阶段 6: 安全审查 ===
        findings = scan_sensitive_info(content)
        if findings:
            log("WARN", "security", f"检测到 {len(findings)} 处可能的敏感信息模式")
            pipeline_result["security_warnings"] = len(findings)
        else:
            log("OK", "security", "敏感信息扫描通过")
        pipeline_result["pipeline_stages"]["security"] = "ok"

        # === 写入文件（write_post 会校验 slug）===
        file_path = write_post(final_slug, content)
        pipeline_result["file"] = str(file_path.relative_to(config.dir))
        # 草稿交还客户端：支持对话内审阅/改写
        pipeline_result["draft"] = content

        # === 构建验证（subprocess，带回真实输出）===
        build_ok, build_msg = hexo_build()
        pipeline_result["build_output"] = build_msg
        if build_ok:
            log("OK", "execute", "构建验证通过")
            pipeline_result["build_status"] = "passed"
        else:
            log("FAIL", "execute", f"构建验证失败: {build_msg}")
            pipeline_result["build_status"] = "failed"
            pipeline_result["status"] = "warning"
            pipeline_result["message"] = f"文章已保存，但构建失败: {build_msg}"
            return pipeline_result

        # === 自动部署（可选）===
        if auto_deploy:
            from droneblog_mcp.core.deploy import auto_deploy_article

            deploy_result = auto_deploy_article(final_slug, content)
            pipeline_result["deploy"] = deploy_result
            deploy_status = deploy_result.get("status")
            if deploy_status == "success":
                log("OK", "deploy", f"自动部署成功: {deploy_result.get('message', '')}")
            elif deploy_status == "skip":
                log("INFO", "deploy", f"跳过自动部署: {deploy_result.get('message', '')}")
            else:
                log("WARN", "deploy", f"自动部署失败: {deploy_result.get('message', '')}")
                pipeline_result["status"] = "warning"
                pipeline_result["message"] = (
                    f"构建通过但部署失败: {deploy_result.get('message', '')}"
                )

        # === 输出规范 ===
        log("OK", "output", f"任务完成: {topic}")
        pipeline_result["pipeline_stages"]["output"] = "ok"
        if not pipeline_result["message"]:
            pipeline_result["message"] = "Blog article generated and verified successfully"

        return pipeline_result

    except Exception as e:
        pipeline_result["status"] = "fail"
        pipeline_result["message"] = str(e)
        log("FAIL", "output", f"任务失败: {e}")
        raise
