# DroneBlog MCP Server - Docker 测试镜像
FROM python:3.11-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# 安装 Hexo CLI
RUN npm install -g hexo-cli

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY droneblog_mcp/ ./droneblog_mcp/
COPY bin/setup-mcp-env.sh ./bin/
COPY .gitignore ./
COPY README.md ./

# 安装 Python 依赖
RUN pip install --no-cache-dir \
    mcp>=1.6.0 \
    pydantic>=2.0 \
    pydantic-settings>=2.0 \
    pyyaml>=6.0 \
    build

# 安装 MCP Server
RUN cd droneblog_mcp && pip install -e .

# 创建测试博客目录
RUN mkdir -p /test-blog/source/_posts
COPY _config.yml /test-blog/
COPY scaffolds/ /test-blog/scaffolds/
COPY source/_posts/ /test-blog/source/_posts/

# 设置环境变量
ENV DRONEBLOG_DIR=/test-blog
ENV PYTHONUNBUFFERED=1

# 暴露 SSE 端口
EXPOSE 8765

# 默认命令
CMD ["droneblog-mcp", "serve", "--transport", "stdio"]
