# ===== BUILDER STAGE =====
# This stage installs all Python dependencies into a virtual environment
FROM python:3.11-slim as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install build dependencies for psycopg2 and other packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev libpq-dev && \
    rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements-prod.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements-prod.txt

# ===== PRODUCTION STAGE ====
# This stage builds the final, lean production image.
FROM python:3.11-slim as production

WORKDIR /app

# Copy the virtual environment with only production dependencies from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies for PostgreSQL client only (no netcat)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

COPY . .



EXPOSE 8000

# Use ENTRYPOINT for your shell script and CMD for the default command
ENTRYPOINT ["/app/app/entrypoint.sh"]
