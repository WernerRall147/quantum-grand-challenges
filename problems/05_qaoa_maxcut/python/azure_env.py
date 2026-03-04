"""Helpers for loading and validating Azure environment settings for QAOA workflows."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict

REQUIRED_KEYS = [
    "AZURE_SUBSCRIPTION_ID",
    "AZURE_RESOURCE_GROUP",
    "AZURE_QUANTUM_WORKSPACE",
    "AZURE_LOCATION",
]

OPTIONAL_DEFAULTS = {
    "AZURE_QUANTUM_PROVIDER": "azure-quantum",
    "AZURE_QUANTUM_TARGET_ID": "microsoft.estimator",
}


class AzureEnvError(ValueError):
    """Raised when Azure environment configuration is missing or invalid."""


def _is_placeholder(value: str) -> bool:
    upper = value.upper()
    return (
        not value.strip()
        or "CHANGE_ME" in upper
        or "<" in value
        or ">" in value
        or upper in {"TODO", "TBD", "REPLACE_ME"}
    )


def load_env_file(path: Path) -> Dict[str, str]:
    if not path.exists():
        raise FileNotFoundError(
            f"Azure env file not found: {path}. Copy .env.azure.example to .env.azure.local and fill it in."
        )

    loaded: Dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        loaded[key.strip()] = value.strip().strip('"').strip("'")
    return loaded


def load_azure_env(env_file: Path) -> Dict[str, str]:
    file_values = load_env_file(env_file)

    merged = dict(file_values)
    for key in REQUIRED_KEYS + list(OPTIONAL_DEFAULTS.keys()):
        if key not in merged and key in os.environ:
            merged[key] = os.environ[key]

    for key, default in OPTIONAL_DEFAULTS.items():
        if key not in merged or not merged[key].strip():
            merged[key] = default

    missing = [key for key in REQUIRED_KEYS if key not in merged]
    if missing:
        raise AzureEnvError(
            "Missing required Azure env keys: " + ", ".join(missing)
        )

    placeholders = [key for key in REQUIRED_KEYS if _is_placeholder(merged[key])]
    if placeholders:
        raise AzureEnvError(
            "Azure env contains placeholder values for: " + ", ".join(placeholders)
        )

    return merged
