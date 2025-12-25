# ===============================
# Stage 1: Builder
# ===============================
FROM python:3.10.19-slim AS builder

# Set working directory
WORKDIR /app

# Copy only dependency file first for better caching
COPY requirements.txt .

# Install dependencies into a temporary directory
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ===============================
# Stage 2: Runner
# ===============================
FROM python:3.10.19-slim AS runner

# Set working directory
WORKDIR /app

# Copy the installed packages from builder stage
COPY --from=builder /install /usr/local

# Copy application code
COPY mcp.py .

# Port to be exposed
EXPOSE 8000

# Run the MCP server with uvicorn
CMD ["uvicorn", "mcp:app", "--host", "0.0.0.0", "--port", "8000"]

#map port 8000 on your local machine (host) to port 8000 inside the container