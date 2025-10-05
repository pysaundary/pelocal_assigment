# syntax=docker/dockerfile:1

FROM python:3.13.7-trixie

# System deps (add build tools only if needed for wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl tini \
  && rm -rf /var/lib/apt/lists/*  

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Workdir
WORKDIR /app

# Install deps separately for better cache hits
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt 

# Copy only backend and static frontend (no venv)
COPY backend /app/backend
COPY static /app/static 
# Non-root runtime user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose backend port (matches .env BACK_END_PORT)
EXPOSE 8000

# Use tini as PID 1 for proper signal handling
ENTRYPOINT ["/usr/bin/tini", "--"]

# Start the app via your launcher (Python 3.13)
CMD ["python", "backend/launch.py"]
