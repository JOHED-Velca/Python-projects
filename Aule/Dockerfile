FROM python:3.11-slim

WORKDIR /app

# System deps (psycopg2 needs these)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

#App code
COPY . /app

EXPOSE 8000
