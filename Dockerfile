FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for wkhtmltopdf and playwright
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    curl \
    unzip \
    gnupg \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libgtk-3-0 \
    libasound2 \
    libnss3 \
    libxss1 \
    libxtst6 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxshmfence1 \
    xdg-utils \
    ca-certificates \
    fonts-liberation \
    lsb-release \
    libappindicator3-1 \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . /app
COPY footballmad-52be88097f72.json /app/footballmad-52be88097f72.json

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Install browsers for Playwright
RUN playwright install --with-deps

CMD ["celery", "-A", "celery_worker.tasks", "worker", "--loglevel=info", "-E"]
