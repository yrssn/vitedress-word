FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=Asia/Tokyo \
    DOCS_DIR=/app/docs

WORKDIR /app

# 系统依赖 + Node.js（用于 vitepress build）
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        tini \
        tzdata \
        gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Python 依赖
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt

# 预装 vitepress 到 docs 目录
RUN mkdir -p /app/docs \
    && cd /app/docs \
    && npm init -y \
    && npm install vitepress --save-dev --no-audit --no-fund

# 复制后端代码
COPY . /app

RUN mkdir -p /app/data /app/uploads

EXPOSE 8013

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${APP_PORT:-8013} --workers ${UVICORN_WORKERS:-2}"]
