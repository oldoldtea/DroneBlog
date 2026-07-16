#!/bin/bash
# DroneBlog MCP Server 环境配置脚本
# 一键配置 Python 3.11 虚拟环境并以“开发模式”安装 MCP Server（pip install -e）。
# 注意：本脚本不再安装任何预构建的 wheel（构建产物不入库），始终从源码安装。

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
echo -e "${YELLOW}[1/5] 检查 Python 3.11+...${NC}"

PYTHON311=""
for cand in python3.12 python3.11 python3; do
    if command -v "$cand" &> /dev/null; then
        # 确认 >= 3.11
        if "$cand" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
            PYTHON311="$cand"
            break
        fi
    fi
done

if [ -z "$PYTHON311" ]; then
    echo -e "${RED}✗ 未找到 Python 3.11+${NC}"
    echo ""
    echo "请安装 Python 3.11 或更高版本："
    echo "  Ubuntu/Debian: sudo apt install python3.11 python3.11-venv python3.11-pip"
    echo "  macOS:         brew install python@3.11"
    echo "  或使用 pyenv:  pyenv install 3.11"
    exit 1
fi

$PYTHON311 --version
echo -e "${GREEN}✓ Python 已找到: $PYTHON311${NC}"
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

# ── 激活虚拟环境并安装 ──
echo -e "${YELLOW}[3/5] 激活虚拟环境并安装 MCP Server（含依赖）...${NC}"

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip > /dev/null 2>&1

# 始终从源码以开发模式安装；pyproject 已声明全部运行依赖（含 requests）。
cd "$MCP_DIR"
pip install -e ".[dev]"
echo -e "${GREEN}✓ 安装成功（pip install -e \".[dev]\"）${NC}"
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

# 关键：确认包可导入（历史上因打包缺模块导致此处 ModuleNotFoundError）
if python -c "import droneblog_mcp; from droneblog_mcp.server import create_server; create_server()" 2>/dev/null; then
    echo -e "${GREEN}✓ 包可正常导入，Server 可实例化${NC}"
else
    echo -e "${RED}✗ 包导入失败，请检查依赖是否完整${NC}"
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
echo "    export DRONEBLOG_GITHUB_TOKEN=ghp_...   # 可选，用于 GitHub 绑定/自动部署"
echo ""
echo "  方式 2: 永久配置（添加到 ~/.bashrc 或 ~/.zshrc）"
echo "    echo 'export DRONEBLOG_DIR=$PROJECT_ROOT' >> ~/.bashrc"
echo "    source ~/.bashrc"
echo ""
echo "  方式 3: 使用 .env 文件（参考 .env.example；.env 已被 .gitignore 排除）"
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "  常用命令："
echo "    source $VENV_DIR/bin/activate   # 激活虚拟环境"
echo "    chmod +x bin/droneblog            # 若 bin/droneblog 无执行权限"
echo "    droneblog-mcp version           # 查看版本"
echo "    droneblog-mcp status            # 查看状态"
echo "    droneblog-mcp serve             # 启动 MCP Server（stdio）"
echo ""
echo "  Claude Desktop 配置示例："
echo "    macOS:   ~/Library/Application Support/Claude/claude_desktop_config.json"
echo "    Windows: %APPDATA%\\Claude\\claude_desktop_config.json"
echo "    详见 droneblog_mcp/README.md"
echo ""
echo -e "${GREEN}  Trellis + MCP 工作流（推荐）${NC}"
echo ""
echo "  1. 所有任务以 Trellis task 形式创建："
echo "       .trellis/tasks/<日期>-<任务名>/"
echo "       包含 prd.md / design.md / implement.md / research/"
echo "  2. 项目规范位于："
echo "       .trellis/spec/guides/index.md"
echo "       .trellis/spec/droneblog_mcp/"
echo "  3. 命令行轻量入口："
echo "       bin/droneblog generate <主题> <分类> <标签1,标签2>"
echo "       bin/droneblog list"
echo "       bin/droneblog build"
echo "       bin/droneblog deploy"
echo "       bin/droneblog status"
echo "  4. 旧 bin/droneblog-pipeline.sh 已重写为 bin/droneblog 的代理，"
echo "     bin/generate-and-archive.sh 已弃用；"
echo "     AI 生成/归档功能由 MCP Server 统一提供。"
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
