# Use Python 3.10 slim image (lightweight, prebuilt wheels compatible)
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Upgrade pip, setuptools, wheel to avoid build errors
RUN pip install --upgrade pip setuptools wheel

# Install dependencies
RUN pip install -r requirements.txt

# Copy all source code
COPY . .

# Expose default port
EXPOSE 8080

# Start FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
