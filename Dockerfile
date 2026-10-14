FROM python:3.12-slim

# Prevent python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install ffmpeg, ca-certificates and curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Ensure downloads directory exists
RUN mkdir -p downloads

# Run bot
CMD ["python", "bot.py"]
