FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy application files
COPY . .

# Create temp directory for downloads
RUN mkdir -p /tmp/telegram_bot_temp

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port (not needed for telegram bot, but good practice)
EXPOSE 8080

# Run the bot
CMD ["python", "bot.py"]