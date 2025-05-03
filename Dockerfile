# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system deps if needed (like build tools)
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copy code
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD ["celery", "-A", "celery_worker.tasks", "worker", "--loglevel=info"]
