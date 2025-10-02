# Stage 1: Build stage with build dependencies
FROM python:3.11-slim as builder

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python build dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


# Stage 2: Final stage with runtime dependencies
FROM python:3.11-slim

# Install Tesseract OCR engine and its language packs
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-all \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from the builder stage and install
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

# Set up a working directory
WORKDIR /app

# Copy your application code
COPY . .

# Expose the port and define the command to run the application
EXPOSE 10000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]