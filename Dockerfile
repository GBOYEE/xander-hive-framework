FROM python:3.10-slim

WORKDIR /app

# Install system deps for Redis client (optional) and clean apt cache
RUN apt-get update && apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default: run a shell (user chooses which agent)
CMD ["bash"]
