FROM python:3.14-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# TARGETARCH is auto-populated by BuildKit/buildx; default it so a legacy
# (DOCKER_BUILDKIT=0) build doesn't produce an empty supercronic-linux- URL.
ARG TARGETARCH=amd64
ARG SUPERCRONIC_VERSION=v0.2.33
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && curl -fsSLo /usr/local/bin/supercronic \
    "https://github.com/aptible/supercronic/releases/download/${SUPERCRONIC_VERSION}/supercronic-linux-${TARGETARCH}" \
 && chmod +x /usr/local/bin/supercronic \
 && apt-get purge -y curl \
 && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .python-version uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

EXPOSE 8000

# Default (web) start: migrate + seed admin + serve. docker-compose overrides
# this per service, so the migrate here only runs on hosts that use the image
# CMD directly (e.g. Render).
CMD ["sh", "/app/deploy/web-entrypoint.sh"]