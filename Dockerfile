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

# generate.py puts /app/tooling on sys.path and imports estimator_config from it. Without
# this the import raises, /api/evaluate swallows it into an empty qsharp_code, and the site
# renders nothing at all - a broken feature that looks like an absent one.
COPY tooling/estimator_config.py /app/tooling/estimator_config.py

# The exemplars generate.py feeds the model, one per algorithm in REFERENCE_IMPLEMENTATIONS.
# Missing files degrade silently to an empty snippet rather than failing, so the generator
# would keep working and quietly get worse.
COPY problems/01_hubbard/qsharp/src/Main.qs /app/problems/01_hubbard/qsharp/src/Main.qs
COPY problems/09_factorization/qsharp/src/Main.qs /app/problems/09_factorization/qsharp/src/Main.qs
COPY problems/19_quantum_chromodynamics/qsharp/src/Main.qs /app/problems/19_quantum_chromodynamics/qsharp/src/Main.qs
COPY problems/18_photovoltaics/qsharp/src/Main.qs /app/problems/18_photovoltaics/qsharp/src/Main.qs
COPY problems/16_error_correction/qsharp/src/Main.qs /app/problems/16_error_correction/qsharp/src/Main.qs
COPY libs/qdk_samples/ /app/libs/qdk_samples/

# Expose port
EXPOSE 8000

# Health check (uses the / endpoint)
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/', timeout=3)" || exit 1

# Run the API
CMD ["uvicorn", "agents.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
