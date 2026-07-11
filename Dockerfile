# DroneBlog MCP Server - 容器镜像
# 以非 editable 方式（pip install .）安装，验证真实打包路径；
# 以非 root 运行；博客目录可写（生成/编辑/删除需要写权限）。

FROM python:3.11-slim

# 系统依赖：git（部署/克隆）、node+npm（Hexo）
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        curl \
        ca-certificates \
        nodejs \
        npm \
    && rm -rf /var/lib/apt/lists/*

# Hexo CLI（用于 build/deploy 工具）
RUN npm install -g hexo-cli

# ── 安装 MCP Server（验证真实打包）──
WORKDIR /build
COPY droneblog_mcp/pyproject.toml droneblog_mcp/README.md ./
COPY droneblog_mcp/src ./src
RUN pip install --no-cache-dir .

# ── 运行时可写博客目录 ──
WORKDIR /test-blog
COPY _config.yml ./
COPY scaffolds/ ./scaffolds/
COPY source/_posts/ ./source/_posts/

# 非 root 运行，并确保博客目录可写
RUN useradd -m -u 1000 app && chown -R app:app /test-blog
USER app

ENV DRONEBLOG_DIR=/test-blog \
    PYTHONUNBUFFERED=1

# SSE 端口（仅 --transport sse 时使用）
EXPOSE 8765

# 默认 stdio（MCP 标准传输）；SSE：docker run ... droneblog-mcp serve --transport sse --host 0.0.0.0
CMD ["droneblog-mcp", "serve", "--transport", "stdio"]
