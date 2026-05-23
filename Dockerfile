FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        nodejs \
        npm \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/uv-venv \
    && /opt/uv-venv/bin/pip install --upgrade pip \
    && /opt/uv-venv/bin/pip install uv \
    && ln -s /opt/uv-venv/bin/uv /usr/local/bin/uv

WORKDIR /app

# Copy the Python project metadata and source first so uv can sync the server env.
COPY server/pyproject.toml server/uv.lock ./server/
COPY server/README.md ./server/README.md
COPY server/src ./server/src

RUN cd /app/server && uv sync --frozen

# Copy the Angular app and install its dependencies.
COPY client/package.json client/package-lock.json ./client/
RUN cd /app/client && npm ci

COPY client ./client
COPY server ./server
COPY ecosystem.config.cjs /app/ecosystem.config.cjs
COPY start-server.sh /app/start-server.sh
COPY docker-entrypoint.sh /app/docker-entrypoint.sh

RUN npm install -g pm2 \
    && cd /app/client && npm run build \
    && chmod +x /app/docker-entrypoint.sh /app/start-server.sh

EXPOSE 4200

CMD ["/app/docker-entrypoint.sh"]
