# Stage 1: Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++

COPY requirements.txt .
# Install wheels to a local directory
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# Stage 2: Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install only the necessary runtime tool (iptables)
RUN apt-get update && \
    apt-get install -y --no-install-recommends iptables && \
    rm -rf /var/lib/apt/lists/*

# Copy wheels from builder and install them
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copy the application code
COPY . .

CMD ["python", "main.py"]
