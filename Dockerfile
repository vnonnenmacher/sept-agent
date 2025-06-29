# Base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    default-mysql-client \
    pkg-config \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Preload model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb')"

# Add wait-for-it script
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh .
RUN chmod +x wait-for-it.sh

# 🚨 Copy project AFTER dependency setup
COPY . .

ENV DJANGO_DEBUG=False
# ✅ Now `manage.py` exists, so this will work
RUN python manage.py collectstatic --noinput

# Expose Django port
EXPOSE 8000
