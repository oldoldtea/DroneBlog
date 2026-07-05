"""DroneBlog MCP Server - Main Entry Point"""

import argparse
import asyncio
import os
import sys

from droneblog_mcp.models.config import DroneBlogConfig, set_config
from droneblog_mcp.server import create_server


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description="DroneBlog MCP Server - AI-powered Hexo blog management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 启动 MCP Server（stdio 模式，默认）
  droneblog-mcp serve

  # 启动 SSE 模式
  droneblog-mcp serve --transport sse --port 8765

  # 指定博客目录
  DRONEBLOG_DIR=/path/to/blog droneblog-mcp serve

Environment Variables:
  DRONEBLOG_DIR         博客工作目录
  OPENAI_API_KEY        OpenAI API Key
  DRONEBLOG_MODEL       默认 AI 模型 (default: gpt-4o-mini)
  DRONEBLOG_TEMPERATURE AI 生成温度 (default: 0.7)
  DRONEBLOG_MAX_TOKENS  最大 token 数 (default: 4000)
  DRONEBLOG_AUTO_CONFIRM 是否跳过人工审核 (default: false)
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
        "--port",
        type=int,
        default=8765,
        help="Port for SSE transport (default: 8765)",
    )
    serve_parser.add_argument(
        "--dir",
        type=str,
        default=".",
        help="Blog working directory (default: current directory)",
    )

    # status 命令
    status_parser = subparsers.add_parser("status", help="Show pipeline status")

    # version 命令
    version_parser = subparsers.add_parser("version", help="Show version")

    args = parser.parse_args()

    if args.command == "version":
        print("droneblog-mcp 0.1.0")
        return 0

    if args.command == "status":
        # 快速显示状态
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

    if args.command == "serve" or args.command is None:
        # 初始化配置
        try:
            # 如果命令行指定了 dir，设置环境变量
            if hasattr(args, "dir") and args.dir:
                os.environ["DRONEBLOG_DIR"] = os.path.abspath(args.dir)

            config = DroneBlogConfig()
            set_config(config)
        except Exception as e:
            print(f"Configuration error: {e}", file=sys.stderr)
            print("\nPlease set DRONEBLOG_DIR to your blog directory:", file=sys.stderr)
            print("  export DRONEBLOG_DIR=/path/to/your/blog", file=sys.stderr)
            return 1

        # 创建并启动 MCP Server
        mcp = create_server()

        print(f"=" * 60)
        print(f"DroneBlog MCP Server")
        print(f"=" * 60)
        print(f"Blog Directory: {config.dir}")
        print(f"Transport: {args.transport}")
        if args.transport == "sse":
            print(f"Port: {args.port}")
        print(f"Model: {config.model}")
        print(f"")
        print(f"Available Tools:")
        print(f"  - blog_generate    生成博客文章")
        print(f"  - blog_list        列出文章")
        print(f"  - blog_read        读取文章")
        print(f"  - blog_edit        编辑文章")
        print(f"  - blog_delete      删除文章")
        print(f"  - config_get       获取配置")
        print(f"  - config_set       修改配置")
        print(f"  - build            构建站点")
        print(f"  - deploy           部署站点")
        print(f"  - pipeline_status  查看流水线状态")
        print(f"  - pipeline_run     执行完整流水线")
        print(f"")
        print(f"Available Resources:")
        print(f"  - blog://{{slug}}    文章内容")
        print(f"  - config://site    站点配置")
        print(f"  - config://theme   主题配置")
        print(f"  - pipeline://log   流水线日志")
        print(f"  - blog://list      文章列表")
        print(f"")
        print(f"Press Ctrl+C to stop")
        print(f"=" * 60)

        try:
            if args.transport == "stdio":
                mcp.run(transport="stdio")
            else:
                mcp.run(transport="sse")
        except KeyboardInterrupt:
            print("\n[INFO] Shutting down...")
            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
