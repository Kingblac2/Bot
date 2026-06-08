# Use official lightweight Python image
FROM python:3.11-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies if required
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

# Copy frontend source code
COPY app.py .

# Streamlit config (optional custom styling can go into a streamlit config directory if needed, but we do inline css)
# Expose Streamlit port
EXPOSE 8501

# Run Streamlit server
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
