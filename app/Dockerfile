FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and templates
COPY . .

# Set default runtime environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=5000 \
    APP_VERSION=v1.0.0

EXPOSE 5000

# Default entrypoint runs web dashboard server; overridden via args for Jobs & CronJobs
CMD ["python", "app.py"]
