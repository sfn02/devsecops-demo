# ===== BUILDER STAGE =====
FROM python:3.11-slim as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app


RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev libpq-dev && \
    rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements-prod.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements-prod.txt

# ===== TEST STAGE =====
FROM python:3.11-slim as tester

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=RendezVous.settings.dev

RUN pytest

# ===== PRODUCTION STAGE =====
FROM python:3.11-slim as production

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

COPY . .

ENV DJANGO_SETTINGS_MODULE=RendezVous.settings.prod

EXPOSE 8000
CMD ["./entrypoint.sh"]
