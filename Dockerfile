# Dockerfile for Detox 30 Bot Refactored
FROM python:3.12-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy source code
COPY src/ ./src/
COPY .env.example .env.example

# Create logs directory
RUN mkdir -p logs

# Set environment
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Expose ports for monitoring
EXPOSE 8080 9090

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Run the bot
CMD ["python", "src/bot.py"]
