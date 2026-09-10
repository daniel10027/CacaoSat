# syntax=docker/dockerfile:1

# --- build : dépendances Python dans un venv ---
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# --- runtime ---
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    FLASK_APP=wsgi.py \
    FLASK_CONFIG=production

RUN apt-get update \
 && apt-get install -y --no-install-recommends libpq5 curl \
 && rm -rf /var/lib/apt/lists/* \
 && groupadd -r app && useradd -r -g app app

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY . .
RUN chmod +x entrypoint.sh && chown -R app:app /app

USER app
EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=3s --start-period=25s --retries=5 \
  CMD curl -fsS http://localhost:8000/api/v1/health || exit 1

ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi:app"]
