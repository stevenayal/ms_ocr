# Multi-stage build for ms-ocr
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Tesseract OCR
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-eng \
    # OpenCV dependencies
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    # Camelot dependencies
    ghostscript \
    python3-tk \
    # Tabula dependencies (Java)
    default-jre \
    # Build tools
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY . .

# Install the package
RUN pip install -e .

# Create directories
RUN mkdir -p /data/input /data/output /app/assets

# Set entrypoint
ENTRYPOINT ["ms-ocr"]

# Default command
CMD ["--help"]


# Development stage
FROM base as dev

# Install development dependencies
RUN pip install pytest pytest-cov ruff black isort mypy

# Override entrypoint for interactive development
ENTRYPOINT ["/bin/bash"]


# Production stage
FROM base as prod

# Copy only necessary files
COPY --from=base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=base /usr/local/bin/ms-ocr /usr/local/bin/ms-ocr
COPY --from=base /app /app

# Run as non-root user
RUN useradd -m -u 1000 msocr && \
    chown -R msocr:msocr /app /data

USER msocr

WORKDIR /data

ENTRYPOINT ["ms-ocr"]
CMD ["--help"]
