FROM mcr.microsoft.com/devcontainers/python:3.11

WORKDIR /app

# Install dependencies
COPY agents/api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full project (agents + knowledge modules)
COPY agents/ /app/agents/
COPY knowledge/ /app/knowledge/
COPY problems/reference_index.json /app/problems/reference_index.json

# Expose port
EXPOSE 8000

# Run the API
CMD ["uvicorn", "agents.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
