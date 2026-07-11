"""DroneBlog MCP Server - Pipeline Tools"""

from mcp.server.fastmcp import FastMCP

from droneblog_mcp.models.config import get_config
from droneblog_mcp.utils.log import log, parse_log_status, read_log_lines


def register_pipeline_tools(mcp: FastMCP) -> None:
    """注册流水线相关 Tools"""

    @mcp.tool()
    async def pipeline_status() -> dict:
        """获取当前流水线执行状态和日志

        Returns:
            流水线状态，包括各阶段执行情况和最近日志
        """
        stages = parse_log_status()
        recent_logs = read_log_lines(50)

        # ready = 最近一次运行没有任何阶段处于 FAIL（日志按阶段记录最后状态）
        pipeline_ready = not any(s.get("status") == "FAIL" for s in stages.values())

        return {
            "status": "success",
            "pipeline_ready": pipeline_ready,
            "stages": stages,
            "recent_logs": recent_logs,
        }

    @mcp.tool()
    async def pipeline_run(
        task_type: str,
        params: dict | None = None,
    ) -> dict:
        """执行完整的 6 阶段 AI 流水线

        Args:
            task_type: 任务类型，可选值: content_creation（内容创作）、config_change（配置调整）、
                      theme_custom（主题定制）、debug_build（问题排查）、deploy（部署发布）
            params: 任务参数，根据任务类型不同而不同
                - content_creation: {topic, category, tags, prompt, model, slug, auto_confirm}
                - config_change: {scope, key, value}
                - theme_custom: {key, value}
                - debug_build: {}
                - deploy: {build_first}

        Returns:
            流水线执行结果
        """
        from droneblog_mcp.core.pipeline import run_pipeline
        from droneblog_mcp.utils.fs import hexo_build
        from droneblog_mcp.utils.yaml import set_site_config

        params = params or {}

        if task_type == "content_creation":
            topic = params.get("topic", "")
            category = params.get("category", "后端开发")
            tags = params.get("tags", []) or []
            prompt = params.get("prompt", "")
            model = params.get("model", "")
            slug = params.get("slug", "")
            auto_confirm = params.get("auto_confirm", True)

            if not topic:
                return {"status": "fail", "message": "Missing required param: topic"}

            # 与 blog_generate 一致的入参校验（单一来源在工具层提前失败）
            config = get_config()
            if category not in config.valid_categories:
                return {
                    "status": "fail",
                    "message": (
                        f"Invalid category '{category}'. Must be one of: {config.valid_categories}"
                    ),
                }
            if not (config.min_tags <= len(tags) <= config.max_tags):
                return {
                    "status": "fail",
                    "message": (
                        f"Tags count {len(tags)} must be between "
                        f"{config.min_tags} and {config.max_tags}"
                    ),
                }

            try:
                result = run_pipeline(
                    topic=topic,
                    category=category,
                    tags=tags,
                    prompt=prompt,
                    model=model or None,
                    slug=slug,
                    auto_confirm=auto_confirm,
                )
                return result
            except Exception as e:
                return {"status": "fail", "message": str(e)}

        elif task_type == "config_change":
            scope = params.get("scope", "site")
            key = params.get("key", "")
            value = params.get("value")

            if not key:
                return {"status": "fail", "message": "Missing required param: key"}

            ok, msg = set_site_config(scope, key, value)
            if ok:
                # 构建验证
                build_ok, build_msg = hexo_build()
                if build_ok:
                    log("OK", "output", "配置修改并构建成功")
                    return {"status": "success", "message": msg, "build": "passed"}
                else:
                    return {"status": "warning", "message": msg, "build": f"failed: {build_msg}"}
            else:
                return {"status": "fail", "message": msg}

        elif task_type == "debug_build":
            build_ok, build_msg = hexo_build()
            if build_ok:
                log("OK", "output", "构建成功，无错误")
                return {"status": "success", "message": "Build successful", "details": build_msg}
            else:
                log("FAIL", "output", f"构建失败: {build_msg}")
                return {"status": "fail", "message": build_msg}

        elif task_type == "deploy":
            build_first = params.get("build_first", True)
            if build_first:
                build_ok, _ = hexo_build()
                if not build_ok:
                    return {"status": "fail", "message": "Build failed before deploy"}

            from droneblog_mcp.utils.fs import hexo_deploy

            deploy_ok, deploy_msg = hexo_deploy()
            if deploy_ok:
                log("OK", "output", "部署成功")
                return {"status": "success", "message": deploy_msg}
            else:
                return {"status": "fail", "message": deploy_msg}

        else:
            return {"status": "fail", "message": f"Unknown task_type: {task_type}"}
