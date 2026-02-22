#!/usr/bin/env python3
"""
Resource Estimator automation for Quantum Grand Challenges.
Runs Azure Quantum Resource Estimator with standardized targets and outputs.
"""

import argparse
import json
import math
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Sequence

try:
    import yaml
except ImportError:  # pragma: no cover - optional dependency
    yaml = None


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "config" / "default.yaml"

# Standard estimator targets
ESTIMATOR_TARGETS = {
    "surface_code_generic_v1": {
        "description": "Generic surface code with standard parameters",
        "error_budget": 0.001,
        "constraints": {"max_duration": "1 hour"}
    },
    "qubit_gate_ns_e3": {
        "description": "Gate-based model, 1us gate time, 1e-3 error rate",
        "error_budget": 0.001,
        "constraints": {"max_duration": "1 day"}
    },
    "qubit_gate_ns_e4": {
        "description": "Gate-based model, 1us gate time, 1e-4 error rate", 
        "error_budget": 0.0001,
        "constraints": {"max_duration": "1 week"}
    }
}


def _require_yaml() -> Any:
    if yaml is None:
        raise RuntimeError("PyYAML is required. Install with `pip install pyyaml`.")
    return yaml


def _load_yaml_file(path: Path) -> Dict[str, Any]:
    parser = _require_yaml()
    with open(path, "r", encoding="utf-8") as handle:
        data = parser.safe_load(handle)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping at root of {path}")
    return data


def _resolve_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


class EstimationManager:
    """Coordinate batch estimation runs driven by config files."""

    def __init__(self, config_path: Path, output_dir: Optional[Path] = None):
        self.repo_root = _resolve_repo_root()
        self.config_path = config_path.resolve()
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        self.config = _load_yaml_file(self.config_path)
        self.output_dir = Path(output_dir) if output_dir else self._default_output_dir()

    def _default_output_dir(self) -> Path:
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        return Path(__file__).resolve().parent / "output" / timestamp

    def _load_instance_details(self, problem: Dict[str, Any], problem_dir: Path) -> Dict[str, Any]:
        instance_cfg = problem.get("instance", {})
        instance_file = instance_cfg.get("file")
        parameters: Dict[str, Any] = {}
        relative_instance_path = None

        if instance_file:
            resolved = (problem_dir / instance_file).resolve()
            if resolved.exists():
                relative_instance_path = str(resolved.relative_to(self.repo_root))
                try:
                    parameters = _load_yaml_file(resolved)
                except Exception as exc:  # pragma: no cover - best effort
                    print(f"Warning: failed to load instance file {resolved}: {exc}", file=sys.stderr)
                    parameters = {}
            else:
                print(f"Warning: instance file not found: {resolved}", file=sys.stderr)

        return {
            "name": instance_cfg.get("name", "default"),
            "description": instance_cfg.get(
                "description",
                f"Default instance for {problem.get('id', 'unknown')}"
            ),
            "parameters": parameters,
            "source": relative_instance_path
        }

    def _resolve_qs_file(self, problem_dir: Path, qs_file: Optional[str]) -> Path:
        if qs_file:
            candidate = (problem_dir / qs_file).resolve()
        else:
            candidate = (problem_dir / "qsharp" / "Program.qs").resolve()
        if not candidate.exists():
            raise FileNotFoundError(f"Q# file not found: {candidate}")
        return candidate

    def run_all(
        self,
        selected_problem_ids: Optional[Sequence[str]] = None,
        selected_targets: Optional[Sequence[str]] = None,
        dry_run: bool = False,
        summary_output: Optional[Path] = None,
        simulate: bool = False
    ) -> Dict[str, Any]:
        problems_cfg = self.config.get("problems", [])
        if not isinstance(problems_cfg, list):
            raise ValueError("Configuration file must define a list under 'problems'.")

        if dry_run:
            mode = "dry-run"
        elif simulate:
            mode = "mock"
        else:
            mode = "live"

        plan: Dict[str, Any] = {
            "generated_at_utc": datetime.utcnow().isoformat() + "Z",
            "config_source": str(self.config_path.relative_to(self.repo_root))
            if self.config_path.is_relative_to(self.repo_root)
            else str(self.config_path),
            "output_dir": str(self.output_dir),
            "mode": mode,
            "problems": []
        }

        for problem in problems_cfg:
            problem_id = problem.get("id")
            if not problem_id:
                print("Warning: skipping unnamed problem in configuration.", file=sys.stderr)
                continue
            if selected_problem_ids and problem_id not in selected_problem_ids:
                continue

            problem_path = problem.get("path") or f"problems/{problem_id}"
            problem_dir = (self.repo_root / problem_path).resolve()
            if not problem_dir.exists():
                print(f"Warning: problem directory not found for {problem_id}: {problem_dir}", file=sys.stderr)
                continue

            qs_file = None
            try:
                qs_file = self._resolve_qs_file(problem_dir, problem.get("qs_file"))
            except FileNotFoundError as exc:
                print(f"Warning: {exc}", file=sys.stderr)
                continue

            estimator = ResourceEstimator(problem_dir)
            instance_details = self._load_instance_details(problem, problem_dir)
            algorithm = problem.get("algorithm", "unknown")
            estimator_params = problem.get("estimator_params", {})
            entry_point = estimator_params.get("entry_point")
            estimator_arguments = estimator_params.get("parameters")
            entry_point_flag = estimator_params.get("entry_point_flag", "--operation")
            extra_cli_args = estimator_params.get("cli_args")
            mock_overrides = estimator_params.get("mock_metrics")
            targets = list(selected_targets) if selected_targets else problem.get("targets", list(ESTIMATOR_TARGETS.keys()))

            problem_entry = {
                "id": problem_id,
                "algorithm": algorithm,
                "instance": instance_details,
                "entry_point": entry_point,
                "simulate": simulate,
                "targets": [],
                "errors": []
            }

            for target in targets:
                if target not in ESTIMATOR_TARGETS:
                    msg = f"Unknown estimator target '{target}' for {problem_id}."
                    print(f"Warning: {msg}", file=sys.stderr)
                    problem_entry["errors"].append({"target": target, "error": msg})
                    continue

                if dry_run:
                    print(f"[PLAN] {problem_id} :: {target} (algorithm={algorithm})")
                    problem_entry["targets"].append({"name": target, "status": "planned"})
                    continue

                print(f"[INFO] Estimating {problem_id} on {target} ...")
                try:
                    result = estimator.run_estimation(
                        target,
                        qs_file=qs_file,
                        instance_params=estimator_arguments,
                        algorithm=algorithm,
                        entry_point=entry_point,
                        entry_point_flag=entry_point_flag,
                        extra_cli_args=extra_cli_args,
                        instance_description=instance_details.get("description"),
                        metadata_parameters=instance_details.get("parameters"),
                        simulate=simulate,
                        mock_overrides=mock_overrides
                    )
                except Exception as exc:  # pragma: no cover - CLI error path
                    print(f"Error: estimation failed for {problem_id} on {target}: {exc}", file=sys.stderr)
                    problem_entry["errors"].append({"target": target, "error": str(exc)})
                    continue

                result_summary = {
                    "name": target,
                    "status": "completed",
                    "metrics": result.get("metrics", {}),
                    "artifact_path": result.get("_metadata", {}).get("artifact_path"),
                    "build": result.get("build", {})
                }
                problem_entry["targets"].append(result_summary)

            plan["problems"].append(problem_entry)

        written_summary_path: Optional[Path] = None

        if not dry_run:
            summary_path = self.output_dir / "summary.json"
            summary_path.parent.mkdir(parents=True, exist_ok=True)
            with open(summary_path, "w", encoding="utf-8") as handle:
                json.dump(plan, handle, indent=2)
            plan["summary_path"] = str(summary_path)
            written_summary_path = summary_path
            print(f"[INFO] Wrote summary to {summary_path}")

        if summary_output:
            summary_output = summary_output.resolve()
            summary_output.parent.mkdir(parents=True, exist_ok=True)
            with open(summary_output, "w", encoding="utf-8") as handle:
                json.dump(plan, handle, indent=2)
            plan["summary_path"] = str(summary_output)
            written_summary_path = summary_output
            print(f"[INFO] Wrote summary to {summary_output}")

        if written_summary_path:
            plan["summary_path"] = str(written_summary_path)

        return plan


class ResourceEstimator:
    """Wrapper for Azure Quantum Resource Estimator."""
    
    def __init__(self, problem_dir: Path):
        self.problem_dir = Path(problem_dir)
        self.estimates_dir = self.problem_dir / "estimates"
        self.estimates_dir.mkdir(exist_ok=True)
        
    def run_estimation(self, 
                      target_name: str,
                      qs_file: Optional[Path] = None,
                      instance_params: Optional[Dict] = None,
                      algorithm: Optional[str] = None,
                      entry_point: Optional[str] = None,
                      entry_point_flag: str = "--operation",
                      extra_cli_args: Optional[Sequence[str]] = None,
                      instance_description: Optional[str] = None,
                      metadata_parameters: Optional[Dict[str, Any]] = None,
                      simulate: bool = False,
                      mock_overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run resource estimation for a given target.
        
        Args:
            target_name: Name of estimator target profile
            qs_file: Path to Q# file (defaults to qsharp/Program.qs)
            instance_params: Problem instance parameters
            entry_point: Optional Q# entry point operation to estimate
            entry_point_flag: CLI flag used to specify the entry point (default: --operation)
            extra_cli_args: Additional CLI arguments to append (e.g., --varepsilon)
            instance_description: Human-readable instance description for metadata
            metadata_parameters: Descriptive parameter set to store in metadata output
            simulate: When True, bypass the Azure CLI and generate mock metrics
            mock_overrides: Optional dictionary providing target-specific mock metrics
            
        Returns:
            Parsed estimation results
        """
        if target_name not in ESTIMATOR_TARGETS:
            raise ValueError(f"Unknown target: {target_name}")
            
        if qs_file is None:
            qs_file = self.problem_dir / "qsharp" / "Program.qs"
            
        if not qs_file.exists():
            raise FileNotFoundError(f"Q# file not found: {qs_file}")
            
        params_file: Optional[Path] = None

        if simulate:
            raw_output = self._generate_mock_output(
                target_name,
                metadata_parameters=metadata_parameters,
                algorithm=algorithm,
                mock_overrides=mock_overrides
            )
        else:
            # Prepare estimation command
            cmd = [
                "qsharp-re",  # Resource Estimator CLI
                "--input", str(qs_file),
                "--target", target_name,
                "--output", "json"
            ]

            if entry_point:
                cmd.extend([entry_point_flag, entry_point])

            if extra_cli_args:
                if isinstance(extra_cli_args, str):
                    cmd.append(extra_cli_args)
                else:
                    cmd.extend(list(extra_cli_args))

            # Add instance parameters if provided
            if instance_params:
                params_file = self.estimates_dir / "temp_params.json"
                with open(params_file, 'w') as f:
                    json.dump(instance_params, f)
                cmd.extend(["--params", str(params_file)])

        try:
            if not simulate:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    raw_output = json.loads(result.stdout)
                except FileNotFoundError:
                    print(
                        "Warning: qsharp-re executable not found. Falling back to mock estimation output.",
                        file=sys.stderr
                    )
                    raw_output = self._generate_mock_output(
                        target_name,
                        metadata_parameters=metadata_parameters,
                        algorithm=algorithm,
                        mock_overrides=mock_overrides
                    )
            # Transform to our standard schema
            
            standardized = self._standardize_output(
                raw_output,
                target_name,
                instance_params,
                algorithm=algorithm,
                instance_description=instance_description,
                metadata_parameters=metadata_parameters
            )
            
            timestamp = datetime.utcnow().isoformat() + "Z"
            output_file = self.estimates_dir / f"{target_name}_{timestamp.replace(':', '')}.json"
            standardized.setdefault("_metadata", {})
            standardized["_metadata"].update({
                "artifact_path": output_file.relative_to(self.problem_dir.parent).as_posix(),
                "generated_at_utc": timestamp
            })

            # Save results
            
            with open(output_file, 'w') as f:
                json.dump(standardized, f, indent=2)
                
            # Update latest.json
            latest_file = self.estimates_dir / "latest.json"
            with open(latest_file, 'w') as f:
                json.dump(standardized, f, indent=2)
                
            return standardized
            
        except subprocess.CalledProcessError as e:
            print(f"Resource estimation failed: {e.stderr}", file=sys.stderr)
            raise
        except json.JSONDecodeError as e:
            print(f"Failed to parse estimator output: {e}", file=sys.stderr)
            raise
        finally:
            # Clean up temp files
            if params_file and params_file.exists():
                params_file.unlink(missing_ok=True)
                
    def _generate_mock_output(
        self,
        target_name: str,
        metadata_parameters: Optional[Dict[str, Any]],
        algorithm: Optional[str],
        mock_overrides: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create deterministic mock estimator output for environments without Azure access."""

        def _as_number(value: Any) -> Optional[float]:
            if isinstance(value, (int, float)):
                return float(value)
            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        overrides: Dict[str, Any] = {}
        if isinstance(mock_overrides, dict):
            if target_name in mock_overrides and isinstance(mock_overrides[target_name], dict):
                overrides = mock_overrides[target_name]
            elif "default" in mock_overrides and isinstance(mock_overrides["default"], dict):
                overrides = mock_overrides["default"]
            elif any(key in mock_overrides for key in [
                "logical_qubits", "physical_qubits", "t_count", "runtime_seconds"
            ]):
                overrides = mock_overrides

        estimated_resources: Dict[str, Any] = {}
        loss_encoding: Dict[str, Any] = {}
        amplitude_settings: Dict[str, Any] = {}
        if isinstance(metadata_parameters, dict):
            maybe_resources = metadata_parameters.get("estimated_resources")
            if isinstance(maybe_resources, dict):
                estimated_resources = maybe_resources
            maybe_loss = metadata_parameters.get("loss_encoding")
            if isinstance(maybe_loss, dict):
                loss_encoding = maybe_loss
            maybe_amp = metadata_parameters.get("amplitude_estimation")
            if isinstance(maybe_amp, dict):
                amplitude_settings = maybe_amp

        loss_qubits = _as_number(loss_encoding.get("num_qubits"))
        precision_qubits = _as_number(amplitude_settings.get("precision_qubits"))

        logical_qubits = overrides.get("logical_qubits")
        if logical_qubits is None:
            logical_qubits = estimated_resources.get("logical_qubits")
        if logical_qubits is None and loss_qubits is not None:
            logical_qubits = loss_qubits
            if precision_qubits is not None:
                logical_qubits += precision_qubits
            logical_qubits += 1  # marker qubit
        if logical_qubits is None:
            logical_qubits = 16
        logical_qubits = int(round(_as_number(logical_qubits) or 16))
        logical_qubits = max(logical_qubits, 1)

        physical_multiplier_map = {
            "surface_code_generic_v1": 1200,
            "qubit_gate_ns_e3": 2200,
            "qubit_gate_ns_e4": 4800
        }
        physical_qubits = overrides.get("physical_qubits")
        if physical_qubits is None:
            physical_qubits = estimated_resources.get("physical_qubits")
        if physical_qubits is None:
            multiplier = physical_multiplier_map.get(target_name, 1500)
            physical_qubits = logical_qubits * multiplier
        physical_qubits = int(round(_as_number(physical_qubits) or logical_qubits * 1500))
        physical_qubits = max(physical_qubits, logical_qubits)

        def _resolve_order(source: Dict[str, Any], key: str, fallback: Optional[float] = None) -> Optional[float]:
            value = _as_number(source.get(key)) if isinstance(source, dict) else None
            return value if value is not None else fallback

        t_count = overrides.get("t_count")
        if t_count is None:
            order = _resolve_order(overrides, "t_count_order")
            if order is None:
                order = _resolve_order(estimated_resources, "t_count_order")
            if order is not None:
                t_count = int(round(math.pow(10.0, order)))
        if t_count is None:
            t_count = int(max(1, logical_qubits ** 4))

        t_depth = overrides.get("t_depth")
        if t_depth is None:
            t_depth = estimated_resources.get("t_depth")
        if t_depth is None:
            t_depth = max(1, int(t_count / max(1, logical_qubits)))

        clifford_count = overrides.get("clifford_count")
        if clifford_count is None:
            clifford_count = estimated_resources.get("clifford_count")
        if clifford_count is None:
            clifford_count = int(t_count * 4)

        runtime_seconds = overrides.get("runtime_seconds")
        if runtime_seconds is None:
            runtime_seconds = estimated_resources.get("runtime_seconds")
        if runtime_seconds is None:
            order = _resolve_order(overrides, "runtime_order")
            if order is None:
                order = _resolve_order(estimated_resources, "runtime_order")
            if order is not None:
                runtime_seconds = int(round(math.pow(10.0, order)))
        if runtime_seconds is None:
            runtime_seconds = int(max(60, logical_qubits * 30))

        return {
            "logicalQubits": logical_qubits,
            "physicalQubits": physical_qubits,
            "tCount": int(t_count),
            "tDepth": int(t_depth),
            "cliffordCount": int(clifford_count),
            "runtimeSeconds": float(runtime_seconds),
            "qdkVersion": "mock",
            "estimatorVersion": f"mock-{target_name}",
            "successProbability": overrides.get("success_probability", 0.99),
            "algorithm": algorithm or overrides.get("algorithm", "unknown")
        }

    def _standardize_output(
        self,
        raw_output: Dict,
        target_name: str,
        instance_params: Optional[Dict],
        algorithm: Optional[str] = None,
        instance_description: Optional[str] = None,
        metadata_parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Convert raw estimator output to our standard schema."""
        
        # Get git commit hash
        try:
            commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], 
                cwd=self.problem_dir.parent,
                text=True
            ).strip()
        except subprocess.CalledProcessError:
            commit = "unknown"
            
        # Extract problem ID from directory name
        problem_id = self.problem_dir.name
        
        # Build standardized result
        result = {
            "problem_id": problem_id,
            "algorithm": algorithm or "unknown",
            "instance": {
                "description": instance_description or f"Default instance for {problem_id}",
                "parameters": metadata_parameters if metadata_parameters is not None else (instance_params or {})
            },
            "estimator_target": target_name,
            "metrics": {
                "logical_qubits": raw_output.get("logicalQubits", 0),
                "physical_qubits": raw_output.get("physicalQubits", 0),
                "t_count": raw_output.get("tCount", 0),
                "t_depth": raw_output.get("tDepth", 0),
                "clifford_count": raw_output.get("cliffordCount", 0),
                "runtime_seconds": raw_output.get("runtimeSeconds", 0)
            },
            "build": {
                "commit": commit,
                "qdk_version": raw_output.get("qdkVersion", "unknown"),
                "estimator_version": raw_output.get("estimatorVersion", "unknown"),
                "date_utc": datetime.utcnow().isoformat() + "Z"
            },
            "notes": f"Estimated using {target_name} target profile"
        }
        
        # Add runtime in days for convenience
        if result["metrics"]["runtime_seconds"] > 0:
            result["metrics"]["runtime_days"] = result["metrics"]["runtime_seconds"] / 86400
            
        return result
        
    def run_parameter_sweep(self, 
                           target_names: List[str],
                           parameter_grid: Dict[str, List]) -> List[Dict[str, Any]]:
        """
        Run estimation across multiple targets and parameter values.
        
        Args:
            target_names: List of estimator targets to use
            parameter_grid: Dict of parameter names to value lists
            
        Returns:
            List of all estimation results
        """
        results = []
        
        # Generate all parameter combinations
        import itertools
        
        param_names = list(parameter_grid.keys())
        param_values = list(parameter_grid.values())
        
        for target in target_names:
            for param_combo in itertools.product(*param_values):
                instance_params = dict(zip(param_names, param_combo))
                
                try:
                    result = self.run_estimation(target, instance_params=instance_params)
                    results.append(result)
                except Exception as e:
                    print(f"Failed estimation for {target} with {instance_params}: {e}", file=sys.stderr)
                    
        return results

def main():
    """CLI interface for resource estimation."""

    parser = argparse.ArgumentParser(description="Run resource estimation for quantum problems")
    parser.add_argument("problem_dir", nargs="?", help="Path to problem directory for single-run mode")
    parser.add_argument("--target", default="surface_code_generic_v1",
                        choices=list(ESTIMATOR_TARGETS.keys()),
                        help="Estimator target profile for single-run mode")
    parser.add_argument("--sweep", action="store_true",
                        help="Run parameter sweep across all targets (single-run mode)")
    parser.add_argument("--params", help="JSON file with instance parameters (single-run mode)")
    parser.add_argument("--config", help="YAML config file defining batch estimation runs")
    parser.add_argument("--all", action="store_true",
                        help="Run all problems defined in the config (uses default config when path omitted)")
    parser.add_argument("--problem", action="append",
                        help="Limit batch runs to specific problem IDs (repeatable)")
    parser.add_argument("--targets", action="append",
                        help="Limit batch runs to specific estimator targets (repeatable)")
    parser.add_argument("--output-dir",
                        help="Directory for summary artifacts when running in batch mode")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print planned batch runs without executing them")
    parser.add_argument("--summary-path",
                        help="Optional path to write combined summary JSON (works with dry-run)")
    parser.add_argument("--mock", action="store_true",
                        help="Simulate estimator outputs instead of calling Azure Resource Estimator")

    args = parser.parse_args()

    batch_mode = bool(args.all or args.config)

    if batch_mode:
        config_path = Path(args.config) if args.config else DEFAULT_CONFIG_PATH
        output_dir = Path(args.output_dir) if args.output_dir else None
        selected_targets = None
        if args.targets:
            selected_targets = []
            for value in args.targets:
                selected_targets.extend([
                    item.strip() for item in value.split(",") if item.strip()
                ])

        selected_problems = None
        if args.problem:
            selected_problems = []
            for value in args.problem:
                selected_problems.extend([
                    item.strip() for item in value.split(",") if item.strip()
                ])

        summary_path = Path(args.summary_path) if args.summary_path else None
        summary = EstimationManager(config_path, output_dir=output_dir).run_all(
            selected_problem_ids=selected_problems,
            selected_targets=selected_targets,
            dry_run=args.dry_run,
            summary_output=summary_path,
            simulate=args.mock
        )
        if args.dry_run:
            print("[INFO] Dry run completed. No estimations executed.")
        else:
            print(f"[INFO] Batch run completed. Summary: {summary.get('summary_path')}")
        return

    if args.targets or args.problem or args.output_dir or args.dry_run or args.summary_path:
        parser.error("Batch-only flags used without --config/--all.")

    if args.mock and args.sweep:
        parser.error("--mock is not supported together with --sweep in single-run mode.")

    if not args.problem_dir:
        parser.error("problem_dir is required in single-run mode.")

    estimator = ResourceEstimator(args.problem_dir)

    # Load instance parameters if provided (accept JSON or YAML).
    instance_params = None
    if args.params:
        params_path = Path(args.params)
        if not params_path.exists():
            raise FileNotFoundError(f"Parameter file not found: {params_path}")

        suffix = params_path.suffix.lower()
        if suffix in {".yaml", ".yml"}:
            instance_params = _load_yaml_file(params_path)
        else:
            with open(params_path, "r", encoding="utf-8") as file_handle:
                instance_params = json.load(file_handle)

    if args.sweep:
        results = estimator.run_parameter_sweep(
            list(ESTIMATOR_TARGETS.keys()),
            {"precision": [0.1, 0.01, 0.001]}
        )
        print(f"Completed parameter sweep: {len(results)} estimations")
    else:
        result = estimator.run_estimation(
            args.target,
            instance_params=instance_params,
            simulate=args.mock
        )
        print(f"Estimation complete: {result['metrics']['logical_qubits']} logical qubits")

if __name__ == "__main__":
    main()
