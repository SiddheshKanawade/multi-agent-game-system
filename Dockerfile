FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make sure the scripts are executable
RUN chmod +x game.py

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "game.py"] 