# Standalone image for the storefront site — a SEPARATE Railway service from the
# bot. Railway's start command uses $PORT; keep it in sync if you change it.
FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway injects $PORT. Shell form so it expands.
CMD uvicorn server:app --host 0.0.0.0 --port ${PORT:-8080}
