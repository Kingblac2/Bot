# Use official lightweight Python image
FROM python:3.11-slim as builder

# Set build directory
WORKDIR /app

# Prevent Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE 1
# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED 1

# Install system dependencies if required (gcc, headers, etc. - lightweight slim has minimal libraries)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file to compile dependencies
COPY requirements.txt .

# Install python dependencies to user directory
RUN pip install --no-cache-dir --user -r requirements.txt


# Final stage
FROM python:3.11-slim as runner

WORKDIR /app

# Copy python packages from builder stage
COPY --from=builder /root/.local /root/.local
COPY requirements.txt .

# Update path to find installed packages
ENV PATH=/root/.local/bin:$PATH

# Copy backend source code (preserving structure)
COPY main.py .
COPY services/ ./services/

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI using uvicorn server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
