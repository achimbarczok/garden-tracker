# syntax=docker/dockerfile:1
FROM --platform=linux/arm64 python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m appuser
USER appuser

ENV PORT=5000
ENV DB_PATH=/data/plants.db

VOLUME ["/data"]
EXPOSE $PORT

CMD ["sh", "-c", "flask run --host=0.0.0.0 --port=$PORT"]
