# Standalone image for the storefront site — a SEPARATE Railway service from the
# bot. server.py reads $PORT itself, so no shell expansion is needed at start.
FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "server.py"]
