# Multi-stage Dockerfile for SS6 Super Student Game
# Optimized for both development and testing environments

# Build stage for compiling dependencies
FROM python:3.13-slim as build

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies and system packages needed for compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    pkg-config \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    libportmidi-dev \
    libjpeg-dev \
    python3-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
WORKDIR /usr/app
RUN python -m venv /usr/app/venv
ENV PATH="/usr/app/venv/bin:$PATH"

# Copy requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.13-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:0

# Create non-root user for security
RUN groupadd -g 999 student && \
    useradd -r -u 999 -g student student

# Install runtime dependencies and display server components
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsdl2-2.0-0 \
    libsdl2-image-2.0-0 \
    libsdl2-mixer-2.0-0 \
    libsdl2-ttf-2.0-0 \
    libfreetype6 \
    libportmidi0 \
    libjpeg62-turbo \
    xvfb \
    xauth \
    x11-xserver-utils \
    pulseaudio \
    && rm -rf /var/lib/apt/lists/*

# Create application directory with proper ownership
RUN mkdir -p /usr/app && \
    chown -R student:student /usr/app

WORKDIR /usr/app

# Copy virtual environment from build stage
COPY --from=build --chown=student:student /usr/app/venv ./venv

# Copy application files with proper ownership
COPY --chown=student:student . .

# Ensure executable permissions for scripts
RUN chmod +x Play.sh || true && \
    chmod +x install.py || true

# Switch to non-root user
USER 999

# Set PATH to include virtual environment
ENV PATH="/usr/app/venv/bin:$PATH"

# Create a startup script that handles display setup
RUN echo '#!/bin/bash\n\
    # Start virtual display if no display is available\n\
    if [ -z "$DISPLAY" ] || ! xset q &>/dev/null; then\n\
    export DISPLAY=:99\n\
    Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset &\n\
    sleep 2\n\
    fi\n\
    \n\
    # Initialize PulseAudio in headless mode\n\
    pulseaudio --start --exit-idle-time=-1 &\n\
    \n\
    # Execute the command passed to the container\n\
    exec "$@"' > /usr/app/entrypoint.sh && \
    chmod +x /usr/app/entrypoint.sh

# Health check to ensure the application can start
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD python -c "import pygame; pygame.init(); print('OK')" || exit 1

# Use the entrypoint script
ENTRYPOINT ["/usr/app/entrypoint.sh"]

# Default command to run the game
CMD ["python", "SS6.origional.py"]

# Metadata labels
LABEL maintainer="SS6 Team"
LABEL description="SS6 Super Student Educational Game - Containerized for testing and deployment"
LABEL version="1.0"
LABEL org.opencontainers.image.source="https://github.com/TeacherEvan/SS7"
LABEL org.opencontainers.image.documentation="https://github.com/TeacherEvan/SS7/blob/main/README.md"