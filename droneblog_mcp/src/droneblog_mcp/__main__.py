"""DroneBlog MCP Server - Main Entry Point"""

import argparse
import getpass
import os
import sys

from droneblog_mcp import __version__
from droneblog_mcp.models.config import DroneBlogConfig, set_config
from droneblog_mcp.server import create_server


def _build_banner(config, transport: str, host: str, port: int) -> str:
    """构造启动信息横幅（仅输出到 stderr，绝不污染 stdout/JSON-RPC 通道）。"""
    lines = [
        "=" * 60,
        f"DroneBlog MCP Server v{__version__}",
        "=" * 60,
        f"Blog Directory: {config.dir}",
        f"Transport: {transport}",
    ]
    if transport == "sse":
        lines.append(f"SSE Endpoint: http://{host}:{port}/sse")
    lines += [
        f"Model: {config.model}",
        f"OpenAI Base URL: {config.openai_base_url}",
        "",
        "Tools (15):",
        "  setup_init / setup_status / setup_sync_posts / setup_update_config",
        "  blog_generate / blog_list / blog_read / blog_edit / blog_delete",
        "  config_get / config_set / build / deploy / pipeline_status / pipeline_run",
        "",
        "Resources:",
        "  blog://{slug}   单篇文章内容",
        "  blogs://list    文章列表",
        "  config://site   站点配置",
        "  config://theme  主题配置",
        "  pipeline://log  流水线日志",
        "=" * 60,
    ]
    return "\n".join(lines)


def _resolve_setup_token(cli_token: str) -> str:
    """解析 setup 使用的 GitHub token：入参 > 环境变量 > TTY 交互输入。"""
    token = (cli_token or "").strip()
    if token:
        print(
            "[warn] 通过命令行传入 --token 会暴露在进程列表中，"
            "建议改用 DRONEBLOG_GITHUB_TOKEN 环境变量。",
            file=sys.stderr,
        )
        return token
    token = os.environ.get("DRONEBLOG_GITHUB_TOKEN", "") or os.environ.get("GITHUB_TOKEN", "")
    if token:
        return token
    if sys.stdin.isatty():
        try:
            return getpass.getpass("GitHub Personal Access Token: ").strip()
        except (EOFError, KeyboardInterrupt):
            return ""
    return ""


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description="DroneBlog MCP Server - AI-powered Hexo blog management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 启动 MCP Server（stdio 模式，默认；stdout 仅承载 JSON-RPC，无额外输出）
  droneblog-mcp serve

  # 启动 SSE 模式
  droneblog-mcp serve --transport sse --host 127.0.0.1 --port 8765

  # 指定博客目录
  DRONEBLOG_DIR=/path/to/blog droneblog-mcp serve

Environment Variables:
  DRONEBLOG_DIR            博客工作目录
  DRONEBLOG_OPENAI_BASE_URL OpenAI 兼容 API 根地址 (default: https://api.openai.com/v1)
  OPENAI_API_KEY           OpenAI API Key
  DRONEBLOG_GITHUB_TOKEN   GitHub PAT（推荐，避免 --token 进 argv）
  DRONEBLOG_MODEL          默认 AI 模型 (default: gpt-4o-mini)
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # serve 命令
    serve_parser = subparsers.add_parser("serve", help="Start MCP Server")
    serve_parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport protocol (default: stdio)",
    )
    serve_parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host for SSE transport (default: 127.0.0.1)",
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Port for SSE transport (default: 8765)",
    )
    serve_parser.add_argument(
        "--dir",
        type=str,
        default=None,
        help="Blog working directory（优先级：--dir > DRONEBLOG_DIR 环境变量 > 当前目录）",
    )
    serve_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="在 stdio 模式下也向 stderr 打印启动横幅（默认 stdio 完全静默）",
    )

    # setup 命令
    setup_parser = subparsers.add_parser("setup", help="Initialize GitHub binding")
    setup_parser.add_argument(
        "--token",
        type=str,
        default="",
        help="GitHub Personal Access Token（不推荐；优先用 DRONEBLOG_GITHUB_TOKEN 环境变量）",
    )
    setup_parser.add_argument(
        "--mode",
        choices=["local", "sync"],
        default="local",
        help="Setup mode: local (manual deploy) or sync (auto GitHub Actions)",
    )

    # status 命令
    subparsers.add_parser("status", help="Show pipeline status")

    # version 命令
    subparsers.add_parser("version", help="Show version")

    args = parser.parse_args()

    if args.command == "version":
        # 非 server 命令，stdout 输出是安全的
        print(f"droneblog-mcp {__version__}")
        return 0

    if args.command == "status":
        # 非 server 命令，stdout 输出是安全的
        try:
            config = DroneBlogConfig()
            set_config(config)
            from droneblog_mcp.utils.log import parse_log_status, read_log_lines

            print(f"DroneBlog Directory: {config.dir}")
            print(f"Posts Directory: {config.posts_dir}")
            print(f"Log File: {config.log_file}")
            print("")
            print("Recent Pipeline Status:")
            stages = parse_log_status()
            for stage, info in stages.items():
                print(f"  [{info['status']}] {stage}: {info['message']}")
            print("")
            print("Recent Logs (last 10):")
            for line in read_log_lines(10):
                print(f"  {line}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        return 0

    if args.command == "setup":
        from droneblog_mcp.core.setup import DroneBlogSetup
        from droneblog_mcp.models.user_config import UserConfig

        token = _resolve_setup_token(args.token)
        if not token:
            print(
                "Error: 未提供 GitHub Token。请设置 DRONEBLOG_GITHUB_TOKEN 环境变量，"
                "或在交互终端中按提示输入。",
                file=sys.stderr,
            )
            return 1

        config = UserConfig(github_token=token)
        setup = DroneBlogSetup(config)
        result = setup.run_setup(args.mode)

        # setup 是 CLI 命令，输出到 stdout 是安全的
        print(f"Setup Result: {result['status']}")
        for step in result.get("steps", []):
            print(f"  {step}")
        if result.get("errors"):
            for err in result["errors"]:
                print(f"  ERROR: {err}")
        if result.get("message"):
            print(f"\n{result['message']}")
        return 0 if result["status"] in ("success", "warning") else 1

    if args.command == "serve" or args.command is None:
        # 初始化配置
        try:
            # 目录优先级：--dir > 已有 DRONEBLOG_DIR 环境变量 > 当前目录（配置默认值 "."）
            # --dir 未显式传入时为 None，绝不覆盖环境变量（MCP 客户端通常在任意 cwd 启动）
            if hasattr(args, "dir") and args.dir:
                os.environ["DRONEBLOG_DIR"] = os.path.abspath(args.dir)

            config = DroneBlogConfig()
            set_config(config)
        except Exception as e:
            # 配置错误输出到 stderr，绝不污染 stdout（stdio 模式下 stdout 是 JSON-RPC 通道）
            print(f"Configuration error: {e}", file=sys.stderr)
            print("\nPlease set DRONEBLOG_DIR to your blog directory:", file=sys.stderr)
            print("  export DRONEBLOG_DIR=/path/to/your/blog", file=sys.stderr)
            return 1

        mcp = create_server()

        # 横幅只输出到 stderr；stdio 默认静默（仅 --verbose 时打印），保证 stdout 纯净
        if args.transport == "sse":
            print(_build_banner(config, args.transport, args.host, args.port), file=sys.stderr)
        elif args.verbose:
            print(_build_banner(config, args.transport, args.host, args.port), file=sys.stderr)

        try:
            if args.transport == "stdio":
                mcp.run(transport="stdio")
            else:
                # 让 --host/--port 真正生效（FastMCP 经 settings 读取）
                mcp.settings.host = args.host
                mcp.settings.port = args.port
                mcp.run(transport="sse")
        except KeyboardInterrupt:
            print("\n[INFO] Shutting down...", file=sys.stderr)
            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
