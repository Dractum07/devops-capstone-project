FROM python:3.12-slim

# Create working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY service/ ./service/

# Run as a non-root user
RUN useradd --uid 1000 theia && chown -R theia /app
USER theia

# Expose the service port and start the app
EXPOSE 8080
CMD ["gunicorn", "--bind=0.0.0.0:8080", "--log-level=info", "service:create_app()"]
