#!/bin/bash
# droneblogctl.sh — DroneBlog Pipeline Service 控制脚本
#
# 用法:
#   ./droneblogctl.sh start    — 启动服务
#   ./droneblogctl.sh stop     — 停止服务
#   ./droneblogctl.sh status   — 查看状态
#   ./droneblogctl.sh restart  — 重启服务
#   ./droneblogctl.sh log      — 查看日志

set -e

SERVICE_NAME="droneblogd"
PID_FILE="/tmp/droneblogd.pid"
LOG_FILE="/tmp/droneblogd.log"
SERVICE_SCRIPT="$(cd "$(dirname "$0")" && pwd)/droneblogd.py"

case "${1:-}" in
  start)
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
      echo "[$SERVICE_NAME] 服务已在运行 (PID: $(cat "$PID_FILE"))"
      exit 0
    fi

    echo "[$SERVICE_NAME] 启动服务..."
    nohup python3 "$SERVICE_SCRIPT" > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    sleep 1

    if kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
      echo "[$SERVICE_NAME] 启动成功 (PID: $(cat "$PID_FILE"))"
      echo "[$SERVICE_NAME] 日志: $LOG_FILE"
      echo "[$SERVICE_NAME] 测试: curl http://127.0.0.1:8765/health"
    else
      echo "[$SERVICE_NAME] 启动失败"
      rm -f "$PID_FILE"
      exit 1
    fi
    ;;

  stop)
    if [ ! -f "$PID_FILE" ]; then
      echo "[$SERVICE_NAME] 服务未运行"
      exit 0
    fi

    PID=$(cat "$PID_FILE")
    echo "[$SERVICE_NAME] 停止服务 (PID: $PID)..."
    kill "$PID" 2>/dev/null || true
    rm -f "$PID_FILE"
    echo "[$SERVICE_NAME] 已停止"
    ;;

  status)
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
      echo "[$SERVICE_NAME] 运行中 (PID: $(cat "$PID_FILE"))"
      curl -s http://127.0.0.1:8765/health 2>/dev/null || echo "[$SERVICE_NAME] 健康检查失败"
    else
      echo "[$SERVICE_NAME] 未运行"
      rm -f "$PID_FILE"
    fi
    ;;

  restart)
    $0 stop
    sleep 1
    $0 start
    ;;

  log)
    if [ -f "$LOG_FILE" ]; then
      tail -f "$LOG_FILE"
    else
      echo "[$SERVICE_NAME] 日志文件不存在"
    fi
    ;;

  *)
    echo "用法: $0 {start|stop|status|restart|log}"
    echo ""
    echo "命令说明:"
    echo "  start   — 启动服务"
    echo "  stop    — 停止服务"
    获取手机号码失败
    
    请确认已关闭Wi-Fi功能
    并已切换至开立证券账户时登记的手机号码使用的蜂窝网络
    已完成网络切换，刷新页面
    echo "  status  — 查看状态"
    echo "  restart — 重启服务"
    echo "  log     — 查看日志"
    exit 1
    ;;
esac
