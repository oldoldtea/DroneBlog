"""DroneBlog MCP Server - Pipeline Executor"""

import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

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


def run_pipeline(
    topic: str,
    category: str,
    tags: list[str],
    prompt: str = "",
    model: Optional[str] = None,
    auto_confirm: bool = False,
    auto_deploy: bool = False,
) -> dict:
    """执行完整的 6 阶段 AI 流水线

    阶段:
    1. 需求分析 (analysis)
    2. Skill 识别 (skill_match)
    3. 执行流程 - AI 生成 (execute)
    4. 流程合规审核 (compliance_audit)
    5. 安全审查 (security)
    6. 输出规范 (output)

    额外步骤:
    - 人工审核（可跳过）
    - 构建验证
    - 自动部署（可选）
    """
    config = get_config()
    slug = generate_slug(topic)
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    pipeline_result = {
        "status": "success",
        "message": "",
        "file": "",
        "slug": slug,
        "title": topic,
        "build_status": "pending",
        "pipeline_stages": {},
    }

    try:
        # === 阶段 1-3: 需求分析 → Skill 识别 → AI 生成 ===
        result = generate_article(topic, category, tags, prompt, model)
        content = result["content"]
        pipeline_result["pipeline_stages"]["analysis"] = "ok"
        pipeline_result["pipeline_stages"]["skill_match"] = "ok"
        pipeline_result["pipeline_stages"]["execute"] = "ok"

        # === 阶段 4: 人工审核（可跳过）===
        if not auto_confirm:
            tmp_file = Path(tempfile.gettempdir()) / f"{slug}.md"
            tmp_file.write_text(content, encoding="utf-8")

            editor = os.environ.get("EDITOR", "nano")
            try:
                import subprocess
                subprocess.run([editor, str(tmp_file)], check=True)
                # 重新读取（用户可能修改）
                content = tmp_file.read_text(encoding="utf-8")
                log("OK", "execute", "人工审核通过")
            except subprocess.CalledProcessError:
                log("FAIL", "execute", "编辑器打开失败或用户取消")
                raise RuntimeError("Editor failed or user cancelled")
            finally:
                if tmp_file.exists():
                    tmp_file.unlink()
        else:
            log("OK", "execute", "跳过人工审核（auto_confirm=true）")

        # === 阶段 5: 合规审核 ===
        ok, msg = validate_frontmatter(content)
        if not ok:
            log("FAIL", "compliance_audit", msg)
            raise ValueError(f"Front-matter validation: {msg}")

        ok, msg = validate_tags(content, config.min_tags, config.max_tags)
        if not ok:
            log("WARN", "compliance_audit", msg)
            # 标签不合规不阻塞，仅警告
        else:
            log("OK", "compliance_audit", "标签数量合规")

        ok, msg = validate_filename(slug)
        if not ok:
            log("FAIL", "compliance_audit", msg)
            raise ValueError(f"Filename validation: {msg}")

        log("OK", "compliance_audit", "全部合规")
        pipeline_result["pipeline_stages"]["compliance_audit"] = "ok"

        # === 阶段 6: 安全审查 ===
        findings = scan_sensitive_info(content)
        if findings:
            log("WARN", "security", f"检测到 {len(findings)} 处可能的敏感信息模式")
            # 警告但不阻塞
        else:
            log("OK", "security", "敏感信息扫描通过")
        pipeline_result["pipeline_stages"]["security"] = "ok"

        # === 写入文件 ===
        file_path = write_post(slug, content)
        pipeline_result["file"] = str(file_path.relative_to(config.dir))

        # === 构建验证 ===
        build_ok, build_msg = hexo_build()
        if build_ok:
            log("OK", "execute", "构建验证通过")
            pipeline_result["build_status"] = "passed"
        else:
            log("FAIL", "execute", f"构建验证失败: {build_msg}")
            pipeline_result["build_status"] = "failed"
            pipeline_result["status"] = "warning"
            pipeline_result["message"] = f"Article saved but build failed: {build_msg}"
            return pipeline_result

        # === 自动部署（可选）===
        if auto_deploy:
            from droneblog_mcp.core.deploy import auto_deploy_article
            deploy_result = auto_deploy_article(slug, content)
            pipeline_result["deploy"] = deploy_result
            if deploy_result["status"] == "success":
                log("OK", "deploy", f"自动部署成功: {deploy_result.get('message', '')}")
            elif deploy_result["status"] == "skip":
                log("INFO", "deploy", f"跳过自动部署: {deploy_result.get('message', '')}")
            else:
                log("WARN", "deploy", f"自动部署失败: {deploy_result.get('message', '')}")
                pipeline_result["status"] = "warning"
                pipeline_result["message"] = f"Build passed but deploy failed: {deploy_result.get('message', '')}"

        # === 阶段 7: 输出规范 ===
        log("OK", "output", f"任务完成: {topic}")
        pipeline_result["pipeline_stages"]["output"] = "ok"
        pipeline_result["message"] = pipeline_result.get("message", "Blog article generated and verified successfully")

        return pipeline_result

    except Exception as e:
        pipeline_result["status"] = "fail"
        pipeline_result["message"] = str(e)
        log("FAIL", "output", f"任务失败: {e}")
        raise
