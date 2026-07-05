#!/bin/bash
# install.sh — DroneBlog Pipeline Service 安装脚本
#
# 用法: ./install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DRONEBLOG_DIR="$(dirname "$SCRIPT_DIR")"
SERVICE_NAME="droneblogd"
USER_SERVICE_DIR="$HOME/.config/systemd/user"
ENV_DIR="$HOME/.config/droneblogd"

echo "========================================"
echo "DroneBlog Pipeline Service Installer"
echo "========================================"
echo ""

# ── 检查依赖 ──
echo "[1/5] 检查依赖..."

if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 未安装"
    exit 1
fi

if ! command -v systemctl &> /dev/null; then
    echo "ERROR: systemd 不可用"
    exit 1
fi

echo "  ✓ python3"
echo "  ✓ systemd"

# ── 创建目录 ──
echo ""
echo "[2/5] 创建目录..."
mkdir -p "$USER_SERVICE_DIR"
mkdir -p "$ENV_DIR"
echo "  ✓ $USER_SERVICE_DIR"
echo "  ✓ $ENV_DIR"

# ── 安装服务文件 ──
echo ""
echo "[3/5] 安装 systemd 服务..."

# 生成服务文件（使用实际路径）
cat > "$USER_SERVICE_DIR/${SERVICE_NAME}.service" << EOF
[Unit]
Description=DroneBlog Pipeline Service
Documentation=https://github.com/oldoldtea/DroneBlog
After=network.target

[Service]
Type=simple
ExecStart=$SCRIPT_DIR/droneblogd.py
ExecReload=/bin/kill -HUP \$MAINPID
Restart=on-failure
RestartSec=5

# 环境变量
Environment="DRONEBLOG_DIR=$DRONEBLOG_DIR"
Environment="DRONEBLOG_PORT=8765"

# 从文件加载 API Key
EnvironmentFile=-$ENV_DIR/env

# 工作目录
WorkingDirectory=$DRONEBLOG_DIR

# 日志
StandardOutput=journal
StandardError=journal
SyslogIdentifier=droneblogd

[Install]
WantedBy=default.target
EOF

echo "  ✓ $USER_SERVICE_DIR/${SERVICE_NAME}.service"

# ── 创建环境变量文件 ──
echo ""
echo "[4/5] 配置环境变量..."

if [ ! -f "$ENV_DIR/env" ]; then
    cat > "$ENV_DIR/env" << 'EOF'
# DroneBlog Pipeline Service 环境变量
# 请填写你的 OpenAI API Key
# 此文件权限已设置为 600，仅当前用户可读

OPENAI_API_KEY=
EOF
    chmod 600 "$ENV_DIR/env"
    echo "  ✓ $ENV_DIR/env (已创建，请编辑填写 API Key)"
else
    echo "  ✓ $ENV_DIR/env (已存在，跳过)"
fi

# ── 重载 systemd ──
echo ""
echo "[5/5] 重载 systemd..."
systemctl --user daemon-reload
echo "  ✓ daemon-reload"

echo ""
echo "========================================"
echo "安装完成"
echo "========================================"
echo ""
echo "后续步骤:"
echo ""
echo "1. 配置 API Key"
echo "   nano ~/.config/droneblogd/env"
echo "   填写: OPENAI_API_KEY=sk-xxx"
echo ""
echo "2. 启动服务"
echo "   systemctl --user start droneblogd"
echo ""
echo "3. 设置开机自启"
echo "   systemctl --user enable droneblogd"
echo ""
echo "4. 查看状态"
echo "   systemctl --user status droneblogd"
echo ""
echo "5. 查看日志"
echo "   journalctl --user -u droneblogd -f"
echo ""
echo "6. 测试服务"
echo "   curl http://127.0.0.1:8765/health"
echo ""
