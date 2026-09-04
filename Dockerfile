FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install optional dependencies for FastAPI/Pydantic features
RUN pip install --no-cache-dir fastapi uvicorn pydantic pytest

COPY . .

# Default: show CLI help. Override CMD for specific commands.
CMD ["python", "cli.py", "--help"]
