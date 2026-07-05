#!/bin/bash
# DroneBlog MCP Server 环境配置脚本
# 一键配置 Python 3.11 虚拟环境并安装 MCP Server

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_ROOT/.venv"
MCP_DIR="$PROJECT_ROOT/droneblog_mcp"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       DroneBlog MCP Server - 环境配置脚本                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ── 检查 Python 3.11 ──
echo -e "${YELLOW}[1/5] 检查 Python 3.11...${NC}"

PYTHON311=""
if command -v python3.11 &> /dev/null; then
    PYTHON311="python3.11"
elif [ -f "$HOME/.local/bin/python3.11" ]; then
    PYTHON311="$HOME/.local/bin/python3.11"
elif [ -f "/usr/local/bin/python3.11" ]; then
    PYTHON311="/usr/local/bin/python3.11"
fi

if [ -z "$PYTHON311" ]; then
    echo -e "${RED}✗ Python 3.11 未找到${NC}"
    echo ""
    echo "请安装 Python 3.11："
    echo "  Ubuntu/Debian: sudo apt install python3.11 python3.11-venv python3.11-pip"
    echo "  macOS: brew install python@3.11"
    echo "  或使用 pyenv: pyenv install 3.11"
    exit 1
fi

$PYTHON311 --version
echo -e "${GREEN}✓ Python 3.11 已找到: $PYTHON311${NC}"
echo ""

# ── 创建虚拟环境 ──
echo -e "${YELLOW}[2/5] 创建虚拟环境...${NC}"

if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}  虚拟环境已存在，跳过创建${NC}"
else
    $PYTHON311 -m venv "$VENV_DIR"
    echo -e "${GREEN}✓ 虚拟环境创建成功: $VENV_DIR${NC}"
fi
echo ""

# ── 激活虚拟环境 ──
echo -e "${YELLOW}[3/5] 激活虚拟环境并安装依赖...${NC}"

source "$VENV_DIR/bin/activate"

# 升级 pip
pip install --upgrade pip > /dev/null 2>&1

# 安装 build 工具（用于打包）
pip install build > /dev/null 2>&1

# 安装 MCP Server（开发模式）
cd "$MCP_DIR"
if [ -f "dist/droneblog_mcp-0.1.0-py3-none-any.whl" ]; then
    # 如果有 wheel 包，直接安装
    pip install "dist/droneblog_mcp-0.1.0-py3-none-any.whl" --force-reinstall
    echo -e "${GREEN}✓ 从 wheel 包安装成功${NC}"
else
    # 否则用开发模式安装
    pip install -e .
    echo -e "${GREEN}✓ 开发模式安装成功${NC}"
fi

echo ""

# ── 验证安装 ──
echo -e "${YELLOW}[4/5] 验证安装...${NC}"

if command -v droneblog-mcp &> /dev/null; then
    VERSION=$(droneblog-mcp version 2>&1)
    echo -e "${GREEN}✓ 命令可用: $VERSION${NC}"
else
    echo -e "${RED}✗ 命令未找到，请检查安装${NC}"
    exit 1
fi

echo ""

# ── 配置环境变量提示 ──
echo -e "${YELLOW}[5/5] 环境配置提示...${NC}"

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  安装完成！请配置以下环境变量：${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "  方式 1: 临时配置（当前终端）"
echo "    export DRONEBLOG_DIR=$PROJECT_ROOT"
echo "    export OPENAI_API_KEY=sk-..."
echo ""
echo "  方式 2: 永久配置（添加到 ~/.bashrc 或 ~/.zshrc）"
echo "    echo 'export DRONEBLOG_DIR=$PROJECT_ROOT' >> ~/.bashrc"
echo "    echo 'export OPENAI_API_KEY=sk-...' >> ~/.bashrc"
echo "    source ~/.bashrc"
echo ""
echo "  方式 3: 使用 .env 文件（项目根目录创建 .env）"
echo "    DRONEBLOG_DIR=$PROJECT_ROOT"
echo "    OPENAI_API_KEY=sk-..."
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "  常用命令："
echo "    source $VENV_DIR/bin/activate   # 激活虚拟环境"
echo "    droneblog-mcp version           # 查看版本"
echo "    droneblog-mcp status            # 查看状态"
echo "    droneblog-mcp serve             # 启动 MCP Server"
echo ""
echo "  Claude Desktop 配置："
echo "    编辑 ~/Library/Application Support/Claude/claude_desktop_config.json"
echo "    添加 mcpServers.droneblog 配置（详见 README）"
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
