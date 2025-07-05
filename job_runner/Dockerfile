FROM python:3.10-slim

WORKDIR /app

# Install system-level dependencies
RUN apt-get update && apt-get install -y build-essential

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the worker script (we'll write this next)
COPY worker.py .

CMD ["python", "worker.py"]
