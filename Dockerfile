FROM python:3.11-slim as python-base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

FROM node:20-slim as frontend-builder

WORKDIR /app

COPY package*.json ./
RUN npm ci # Install all dependencies including devDependencies

COPY client/ ./client/
COPY shared/ ./shared/
COPY vite.config.ts tsconfig.json tailwind.config.ts postcss.config.mjs vite-plugin-meta-images.ts ./
COPY drizzle.config.ts ./
COPY attached_assets/ ./attached_assets/
COPY server/ ./server/

RUN npm run build

FROM python-base as backend-builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM python-base as production

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash appuser

WORKDIR /app

COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

COPY backend/ ./backend/
COPY manage.py ./
COPY --from=frontend-builder /app/dist ./dist/
COPY server/ ./server/

RUN mkdir -p /app/staticfiles && \
    python manage.py collectstatic --noinput 2>/dev/null || true

RUN chown -R appuser:appuser /app
USER appuser

ENV DJANGO_SETTINGS_MODULE=backend.settings \
    USE_GUNICORN=true \
    GUNICORN_WORKERS=4 \
    GUNICORN_THREADS=2 \
    GUNICORN_TIMEOUT=120 \
    PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/auth/me/ || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--worker-class", "gthread", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "backend.wsgi:application"]
