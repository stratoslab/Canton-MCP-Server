FROM python:3.10-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY . .

# Install dependencies
RUN uv sync

# Expose port
EXPOSE 8000

# Run the server with HTTP mode enabled
CMD ["uv", "run", "src/server.py", "--http", "--host", "0.0.0.0", "--port", "8000"]
