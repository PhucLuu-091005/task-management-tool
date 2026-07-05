FROM python:3.14-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ARG TARGETARCH
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

CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]