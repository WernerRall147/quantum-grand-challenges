"""Quantum run records bind results to the exact source and QIR input."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from jsonschema import FormatChecker
from jsonschema import validate

from tooling.quantum_provenance import (
    build_run_provenance,
    problem_submission_source_files,
    target_profile_for_target,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads(
    (ROOT / "tooling" / "schema" / "quantum_run_provenance.json").read_text(
        encoding="utf-8"
    )
)


def _submission_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "manifest_version": "1.0",
                "problem_id": "03_qae_risk",
                "instance_id": "small",
                "depth": 1,
                "backend": {
                    "target_id": "ionq.simulator",
                    "job_name": "readiness-test",
                },
                "execution": {"refined_shots": 32, "trials": 1},
                "submission": {},
                "evidence": {"primary_artifact": "test"},
            }
        ),
        encoding="utf-8",
    )
    env_file = tmp_path / ".env.azure"
    env_file.write_text(
        "\n".join(
            [
                "AZURE_SUBSCRIPTION_ID=00000000-0000-0000-0000-000000000000",
                "AZURE_RESOURCE_GROUP=test-rg",
                "AZURE_QUANTUM_WORKSPACE=test-workspace",
                "AZURE_LOCATION=eastus",
            ]
        ),
        encoding="utf-8",
    )
    job_input = tmp_path / "program.qir"
    job_input.write_bytes(b"example qir\r\nwith binary \x00 bytes")
    return manifest, env_file, job_input


def test_public_run_provenance_has_source_and_qir_hashes():
    kernel = (
        ROOT / "problems" / "01_hubbard" / "qsharp" / "HardwareKernel.qs"
    )
    record = build_run_provenance(
        repo_root=ROOT,
        problem_id="01_hubbard",
        entry_point="HubbardQPEKernel",
        source_paths=[kernel],
        execution_mode="local-simulator",
        target_id=None,
        target_profile="Adaptive_RI",
        shots=128,
        status="succeeded",
        qir="fake-qir-for-hash",
    )

    validate(record, SCHEMA, format_checker=FormatChecker())
    assert record["qir_sha256"] == hashlib.sha256(
        b"fake-qir-for-hash"
    ).hexdigest()
    assert record["source_files"][
        "problems/01_hubbard/qsharp/HardwareKernel.qs"
    ]
    assert "job_id" not in record
    assert record["target_profile"] == "Adaptive_RI"


def test_target_profiles_follow_provider_capabilities():
    assert target_profile_for_target("quantinuum.sim.h2-1e") == "Adaptive_RI"
    assert target_profile_for_target("ionq.simulator") == "Base"
    assert target_profile_for_target("rigetti.sim.qvm") == "Base"
    assert target_profile_for_target("microsoft.estimator") is None


def test_submission_sources_include_root_level_hardware_adapters():
    files = problem_submission_source_files(
        ROOT / "problems" / "01_hubbard" / "qsharp"
    )

    assert ROOT / "problems" / "01_hubbard" / "qsharp" / (
        "VqeHardwareKernel.qs"
    ) in files


def test_generic_dry_run_stamps_private_manifest_provenance(tmp_path: Path):
    manifest, env_file, job_input = _submission_fixture(tmp_path)

    subprocess.run(
        [
            sys.executable,
            "tooling/azure/submit_job_auto.py",
            "--manifest",
            str(manifest),
            "--env-file",
            str(env_file),
            "--job-input-file",
            str(job_input),
            "--target-id",
            "ionq.simulator",
            "--entry-point",
            "QaeKernel",
            "--shots",
            "32",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    stamped = json.loads(manifest.read_text(encoding="utf-8"))
    provenance = stamped["provenance"]
    validate(provenance, SCHEMA, format_checker=FormatChecker())
    assert provenance["status"] == "not_submitted"
    assert provenance["execution_mode"] == "azure-quantum"
    assert provenance["target_profile"] is None
    assert provenance["expected_target_profile"] == "Base"
    assert provenance["input_sha256"] == hashlib.sha256(
        job_input.read_bytes()
    ).hexdigest()
    assert "problems/archived/03_qae_risk/qsharp/HardwareKernel.qs" in (
        provenance["source_files"]
    )
    assert "job_id" not in provenance


def test_execute_requires_an_explicit_compilation_profile(tmp_path: Path):
    manifest, env_file, job_input = _submission_fixture(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "tooling/azure/submit_job_auto.py",
            "--manifest",
            str(manifest),
            "--env-file",
            str(env_file),
            "--job-input-file",
            str(job_input),
            "--target-id",
            "ionq.simulator",
            "--execute",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "--target-profile is required with --execute" in result.stderr


def test_submission_rejects_a_profile_incompatible_with_the_target(
    tmp_path: Path,
):
    manifest, env_file, job_input = _submission_fixture(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "tooling/azure/submit_job_auto.py",
            "--manifest",
            str(manifest),
            "--env-file",
            str(env_file),
            "--job-input-file",
            str(job_input),
            "--target-id",
            "ionq.simulator",
            "--target-profile",
            "Adaptive_RI",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "requires Base" in result.stderr
