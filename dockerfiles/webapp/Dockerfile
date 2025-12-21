# Use Python Alpine as base image
FROM python:3.13.9-alpine

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Set work directory
WORKDIR /financio

# Install system dependencies required for Django and PostgreSQL
RUN apk add --no-cache \
    postgresql-dev \
    gcc \
    musl-dev \
    linux-headers \
    libffi-dev

# Install uv package manager
RUN pip install --no-cache-dir uv

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies using uv
RUN uv pip install --no-cache -r requirements.txt

# Copy project files
COPY . .

# Expose port 8000 for Django
EXPOSE 8000

# Run Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
