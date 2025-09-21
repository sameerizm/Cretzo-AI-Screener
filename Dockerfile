# Use a stable Python version compatible with PyTorch CPU
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Upgrade pip, setuptools, and wheel
RUN pip install --upgrade pip setuptools wheel

# Install PyTorch CPU wheels separately
RUN pip install torch==2.8.0+cpu torchvision==0.21.0+cpu torchaudio==2.8.0+cpu --extra-index-url https://download.pytorch.org/whl/cpu

# Copy requirements (without torch)
COPY requirements.txt .

# Install remaining dependencies
RUN pip install -r requirements.txt

# Copy your app code
COPY . .

# Expose port for Render
EXPOSE 10000

# Start command
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]
