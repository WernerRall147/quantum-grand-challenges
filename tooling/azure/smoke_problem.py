"""Run shared Azure smoke workflow for any problem."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def _resolve(path_arg: str) -> Path:
    path = Path(path_arg)
    if path.is_absolute():
        return path
    return (Path.cwd() / path).resolve()


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run shared Azure smoke workflow for a problem.")
    parser.add_argument("--problem", required=True)
    parser.add_argument("--instance", default="small")
    parser.add_argument("--depth", type=int, default=1)
    parser.add_argument("--shots", type=int, default=256)
    parser.add_argument("--trials", type=int, default=1)
    parser.add_argument("--target-id", default="microsoft.estimator")
    parser.add_argument("--env-file", required=True)
    parser.add_argument("--evidence-file", default=None)
    parser.add_argument("--job-input-file", default=None)
    parser.add_argument("--job-input-format", default="qir.v1")
    parser.add_argument("--entry-point", default=None)
    parser.add_argument("--execute", action="store_true", default=False)
    parser.add_argument("--collect", action="store_true", default=False)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    manifest = root / "problems" / args.problem / "estimates" / f"azure_job_manifest_{args.instance}_d{args.depth}.json"

    py = str(Path(__file__).resolve().parent)
    env_file = str(_resolve(args.env_file))

    validate_env_cmd = ["python", f"{py}/validate_azure_env.py", "--env-file", env_file]
    validate_cli_cmd = ["python", f"{py}/validate_azure_cli.py", "--env-file", env_file]
    manifest_cmd = [
        "python", f"{py}/prepare_problem_manifest.py",
        "--problem", args.problem,
        "--instance", args.instance,
        "--depth", str(args.depth),
        "--shots", str(args.shots),
        "--trials", str(args.trials),
        "--target-id", args.target_id,
    ]
    if args.evidence_file:
        manifest_cmd.extend(["--evidence-file", str(_resolve(args.evidence_file))])

    submit_cmd = [
        "python", f"{py}/submit_job_auto.py",
        "--manifest", str(manifest),
        "--env-file", env_file,
        "--target-id", args.target_id,
        "--job-input-format", args.job_input_format,
    ]
    if args.job_input_file:
        submit_cmd.extend(["--job-input-file", str(_resolve(args.job_input_file))])
    if args.entry_point:
        submit_cmd.extend(["--entry-point", args.entry_point])
    if args.execute:
        submit_cmd.append("--execute")

    report_cmd = [
        "python", f"{py}/write_smoke_report.py",
        "--manifest", str(manifest),
        "--mode", "execute" if args.execute else "dry-run",
    ]
    if args.collect:
        report_cmd.append("--collect-enabled")

    try:
        print("[1/5] validate env")
        _run(validate_env_cmd)
        print("[2/5] validate azure cli")
        _run(validate_cli_cmd)
        print("[3/5] prepare manifest")
        _run(manifest_cmd)
        print("[4/5] submit (dry-run unless --execute)")
        _run(submit_cmd)

        if args.execute and args.collect:
            collect_cmd = [
                "python", f"{py}/collect_job.py",
                "--manifest", str(manifest),
                "--env-file", env_file,
                "--fetch-from-azure",
            ]
            print("[4b/5] collect status")
            _run(collect_cmd)
            report_cmd.append("--collect-attempted")

        print("[5/5] write smoke report")
        _run(report_cmd)
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"Smoke workflow failed at step command: {' '.join(exc.cmd)}")

    print("Azure smoke workflow completed")
    print(f"  problem: {args.problem}")
    print(f"  manifest: {manifest}")


if __name__ == "__main__":
    main()
