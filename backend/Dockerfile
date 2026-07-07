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

# Render (and most PaaS) inject the port to bind on via $PORT; default to 8000 for
# local `docker run`. Migrate + create_admin + collectstatic run on boot so a fresh
# deploy is self-contained; WhiteNoise serves the collected static (gunicorn won't).
# create_admin seeds/promotes the bootstrap admin from INITIAL_ADMIN_* (no-op when
# unset), covering hosts whose pre-deploy hook is paid-only (e.g. Render free tier).
ENV DJANGO_SETTINGS_MODULE=core.settings.production
CMD ["sh", "-c", "uv run python manage.py migrate --noinput && uv run python manage.py create_admin && uv run python manage.py collectstatic --noinput && exec uv run gunicorn core.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]
