FROM python:3.11-slim

WORKDIR /app

# Install Azure CLI + Bicep for `az bicep build` validation in BicepWorkspaceGenerator.
# Uses the Microsoft installer for the slim image footprint.
# libicu is required by the dotnet runtime that backs `az bicep build`.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates gpg libicu-dev \
    && curl -sL https://aka.ms/InstallAzureCLIDeb | bash \
    && az bicep install \
    && apt-get purge -y curl gpg \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY agents/api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full project (agents + knowledge modules)
COPY agents/ /app/agents/
COPY knowledge/ /app/knowledge/
COPY problems/reference_index.json /app/problems/reference_index.json

# Expose port
EXPOSE 8000

# Health check (uses the / endpoint)
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/', timeout=3)" || exit 1

# Run the API
CMD ["uvicorn", "agents.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
