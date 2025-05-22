FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*



COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements-prod.txt



COPY . .



EXPOSE 8000

CMD ["./entrypoint.sh"]
