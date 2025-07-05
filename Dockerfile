# Stage 1: Build stage
FROM python:3.9-slim-bullseye AS builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libdmtx0b \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set up Python environment
WORKDIR /app
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.9-slim-bullseye

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libdmtx0b \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python environment
COPY --from=builder /opt/venv /opt/venv

# Set up environment
WORKDIR /app
ENV PATH="/opt/venv/bin:$PATH"

# Copy application
COPY datamatrix_decoder.py /usr/local/bin/
RUN chmod +x /usr/local/bin/datamatrix_decoder.py

# Create a directory for input files
WORKDIR /data

ENTRYPOINT ["python", "/usr/local/bin/datamatrix_decoder.py"]
