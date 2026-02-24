#!/usr/bin/env python3
"""
Analysis and visualization for QAE Risk Analysis results.
Combines quantum and classical results for comparison.
"""

import argparse
import json
import math
import re
import statistics
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import subprocess
import sys
import yaml


DEFAULT_QAE_PARAMS: Dict[str, Any] = {
    "loss_qubits": 4,
    "threshold": 2.5,
    "mean": 0.0,
    "std_dev": 1.0,
    "precision_bits": 6,
    "repetitions": 120,
    "run_sanity_check": False,
}

class QAERiskAnalyzer:
    """Analyzer for quantum amplitude estimation risk analysis results."""
    
    def __init__(self, problem_dir: str | None = None, show_plots: bool = False):
        script_dir = Path(__file__).resolve().parent
        if problem_dir is None:
            self.problem_dir = script_dir.parent
        else:
            candidate = Path(problem_dir)
            if not candidate.is_absolute():
                candidate = (script_dir / candidate).resolve()
            self.problem_dir = candidate

        self.estimates_dir = self.problem_dir / "estimates"
        self.plots_dir = self.problem_dir / "plots"
        self.estimates_dir.mkdir(exist_ok=True)
        self.plots_dir.mkdir(exist_ok=True)
        self.show_plots = show_plots
        self.latest_quantum_result: Optional[Dict[str, Any]] = None

    def _has_positive_values(self, values) -> bool:
        for value in values:
            try:
                if float(value) > 0:
                    return True
            except (TypeError, ValueError):
                continue
        return False

    def _apply_safe_log_scale(self, axis, values, label_suffix: str = " (linear)") -> None:
        if self._has_positive_values(values):
            axis.set_yscale('log')
        else:
            axis.set_ylabel(f"{axis.get_ylabel()}{label_suffix}")
            axis.set_ylim(bottom=0.0)
        
    def load_estimation_results(self) -> List[Dict[str, Any]]:
        """Load all available estimation results."""
        results = []
        
        if self.estimates_dir.exists():
            for json_file in self.estimates_dir.glob("quantum*.json"):
                try:
                    with open(json_file) as f:
                        result = json.load(f)
                    result['source_file'] = json_file.name
                    results.append(result)
                except Exception as e:
                    print(f"Warning: Could not load {json_file}: {e}")

            # Keep report ordering stable and ensure "latest" points to newest timestamped result.
            results.sort(key=lambda result: (str(result.get("timestamp", "")), str(result.get("source_file", ""))))
                    
        return results
        
    def load_classical_results(self) -> Dict[str, Any]:
        """Load classical baseline results."""
        classical_file = self.estimates_dir / "classical_baseline.json"
        
        if classical_file.exists():
            with open(classical_file) as f:
                return json.load(f)
        else:
            print("Warning: No classical baseline results found")
            return {}
            
    def run_quantum_estimation(
        self,
        skip_build: bool = False,
        qae_params: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Run the Q# quantum estimation and return the parsed result payload."""
        qsharp_dir = self.problem_dir / "qsharp"
        self.latest_quantum_result = None
        effective_params = dict(DEFAULT_QAE_PARAMS)
        if qae_params:
            effective_params.update(qae_params)

        runtime_config_script = self.problem_dir / "python" / "write_runtime_config.py"
        runtime_config_command = [
            sys.executable,
            str(runtime_config_script),
            "--loss-qubits",
            str(int(effective_params["loss_qubits"])),
            "--threshold",
            str(float(effective_params["threshold"])),
            "--mean",
            str(float(effective_params["mean"])),
            "--std-dev",
            str(float(effective_params["std_dev"])),
            "--precision-bits",
            str(int(effective_params["precision_bits"])),
            "--repetitions",
            str(int(effective_params["repetitions"])),
            "--run-sanity-check",
            "true" if bool(effective_params["run_sanity_check"]) else "false",
        ]
        
        if not qsharp_dir.exists():
            print("Q# directory not found")
            return None
            
        try:
            if not skip_build:
                subprocess.run(
                    runtime_config_command,
                    cwd=runtime_config_script.parent,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                print("Building Q# project...")
                build_result = subprocess.run(
                    ["dotnet", "build", "--configuration", "Release"],
                    cwd=qsharp_dir,
                    check=True,
                    capture_output=True,
                    text=True,
                )

                if build_result.stdout:
                    print(build_result.stdout.strip())
                if build_result.stderr:
                    print(build_result.stderr.strip(), file=sys.stderr)
            else:
                subprocess.run(
                    runtime_config_command,
                    cwd=runtime_config_script.parent,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                print("Skipping build; reusing previous Q# compilation artifacts.")
            
            print("Running quantum estimation...")
            # Build is already handled above; always run without rebuilding to reduce noise.
            run_command = ["dotnet", "run", "--configuration", "Release", "--no-build"]

            run_result = subprocess.run(
                run_command,
                cwd=qsharp_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            
            raw_stdout = run_result.stdout
            stdout_clean = raw_stdout.replace("Â±", "±").replace("Â", "").strip()
            if stdout_clean:
                print(stdout_clean)
            if run_result.stderr:
                print(run_result.stderr.strip(), file=sys.stderr)

            histogram_counts: Dict[int, int] = {}
            histogram_denominator: Optional[int] = None
            for match in re.finditer(r"^\s+Phase\s+(\d+)/(\d+).*:\s+(\d+)\s+times$", stdout_clean, flags=re.MULTILINE):
                outcome = int(match.group(1))
                histogram_denominator = int(match.group(2))
                count = int(match.group(3))
                histogram_counts[outcome] = count

            number_pattern = r"([0-9eE+\-\.,]+)"
            config_match = re.search(r"phase bits=([0-9]+), repeats=([0-9]+)", stdout_clean)
            precision_match = re.search(r"Precision qubits:\s*([0-9]+)", stdout_clean)
            repetitions_match = re.search(r"Repetitions:\s*([0-9]+)", stdout_clean)
            threshold_match = re.search(rf"Loss threshold:\s*{number_pattern}", stdout_clean)
            loss_qubits_match = re.search(r"Loss distribution qubits:\s*([0-9]+)", stdout_clean)
            total_qubits_match = re.search(r"Total qubits:\s*([0-9]+)", stdout_clean)
            plus_minus_pattern = r"(?:Â?±|\+/-)"
            quantum_match = re.search(rf"Quantum amplitude estimation.*: {number_pattern} {plus_minus_pattern} {number_pattern}", stdout_clean)
            if quantum_match is None:
                quantum_match = re.search(rf"Mean amplitude estimate:\s*{number_pattern}\s*{plus_minus_pattern}\s*{number_pattern}", stdout_clean)
            analytic_match = re.search(rf"Analytical probability:\s*{number_pattern}", stdout_clean)
            if analytic_match is None:
                analytic_match = re.search(rf"Theoretical tail probability:\s*{number_pattern}", stdout_clean)
            classical_match = re.search(rf"Classical Monte Carlo estimate: {number_pattern} {plus_minus_pattern} {number_pattern}", stdout_clean)
            if classical_match is None:
                classical_match = re.search(rf"Monte Carlo \([0-9]+ samples\):\s*{number_pattern}\s*{plus_minus_pattern}\s*{number_pattern}", stdout_clean)
            difference_match = re.search(rf"Difference between quantum and analytical:\s*{number_pattern}", stdout_clean)

            def to_float(value: str | None) -> float | None:
                if value is None:
                    return None
                try:
                    normalized = value.strip()
                    # Q# output can use locale decimal commas (for example, 0,1897).
                    if "," in normalized and "." not in normalized:
                        normalized = normalized.replace(",", ".")
                    elif "," in normalized and "." in normalized:
                        normalized = normalized.replace(",", "")
                    return float(normalized)
                except ValueError:
                    return None

            quantum_estimate = to_float(quantum_match.group(1) if quantum_match else None)
            quantum_std = to_float(quantum_match.group(2) if quantum_match else None)
            analytic_prob = to_float(analytic_match.group(1) if analytic_match else None)
            classical_prob = to_float(classical_match.group(1) if classical_match else None)
            classical_std = to_float(classical_match.group(2) if classical_match else None)
            difference = to_float(difference_match.group(1) if difference_match else None)
            phase_bits = int(config_match.group(1)) if config_match else None
            repeats = int(config_match.group(2)) if config_match else None
            if phase_bits is None and precision_match:
                phase_bits = int(precision_match.group(1))
            if repeats is None and repetitions_match:
                repeats = int(repetitions_match.group(1))
            if phase_bits is None and histogram_denominator and histogram_denominator > 0:
                phase_bits = int(round(math.log2(histogram_denominator)))
            shots = repeats

            threshold = to_float(threshold_match.group(1) if threshold_match else None)
            loss_qubits = int(loss_qubits_match.group(1)) if loss_qubits_match else None

            if difference is None and quantum_estimate is not None and analytic_prob is not None:
                difference = quantum_estimate - analytic_prob

            circular_amplitude = None
            circular_phase = None
            if histogram_counts and phase_bits is not None:
                total_counts = sum(histogram_counts.values())
                if total_counts > 0:
                    denom = 1 << phase_bits
                    complex_sum = 0.0 + 0.0j
                    for outcome, count in histogram_counts.items():
                        folded_outcome = min(outcome, denom - outcome)
                        angle = 2.0 * math.pi * folded_outcome / denom
                        complex_sum += count * complex(math.cos(angle), math.sin(angle))
                    complex_mean = complex_sum / total_counts
                    if abs(complex_mean) > 1e-12:
                        raw_phase = math.atan2(complex_mean.imag, complex_mean.real)
                        if raw_phase < 0.0:
                            raw_phase += 2.0 * math.pi
                        normalized_phase = raw_phase / (2.0 * math.pi)
                        folded_phase = min(normalized_phase, 1.0 - normalized_phase)
                        theta = math.pi * folded_phase
                        circular_amplitude = math.sin(theta) ** 2
                        circular_phase = folded_phase

            if quantum_estimate is not None:
                self.estimates_dir.mkdir(exist_ok=True)
                total_qubits = int(total_qubits_match.group(1)) if total_qubits_match else None
                if total_qubits is None and phase_bits is not None and loss_qubits is not None:
                    # Risk register + counting register + one marker qubit.
                    total_qubits = loss_qubits + phase_bits + 1

                logical_qubits = total_qubits
                physical_qubits = logical_qubits
                t_count = None
                if phase_bits is not None and repeats is not None:
                    t_count = max(1, phase_bits * repeats * 4)

                result_payload: Dict[str, Any] = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "algorithm": "QPEAmplitudeEstimation",
                    "estimator_target": f"TailRisk > {threshold}" if threshold is not None else "TailRisk",
                    "instance": {
                        "parameters": {
                            "shots": shots,
                            "phase_bits": phase_bits,
                            "repetitions": repeats,
                            "threshold": threshold,
                            "loss_qubits": loss_qubits,
                            "mean": float(effective_params["mean"]),
                            "std_dev": float(effective_params["std_dev"]),
                            "run_sanity_check": bool(effective_params["run_sanity_check"]),
                        }
                    },
                    "metrics": {
                        "logical_qubits": logical_qubits if logical_qubits is not None else "N/A",
                        "physical_qubits": physical_qubits if physical_qubits is not None else "N/A",
                        "t_count": t_count if t_count is not None else "N/A",
                        "runtime_days": 0,
                        "phase_bits": phase_bits,
                        "repetitions": repeats,
                        "quantum_estimate": quantum_estimate,
                        "quantum_std_error": quantum_std,
                        "analytic_probability": analytic_prob,
                        "classical_estimate": classical_prob,
                        "classical_std_error": classical_std,
                        "difference": difference,
                        "circular_phase": circular_phase,
                        "circular_amplitude": circular_amplitude,
                    },
                    "raw_output": stdout_clean,
                }

                if histogram_counts:
                    result_payload["histogram_counts"] = histogram_counts

                output_path = self.estimates_dir / "quantum_estimate.json"
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result_payload, f, indent=2)
                print(f"Saved quantum estimation results to {output_path}")
                self.latest_quantum_result = result_payload
                return result_payload
            else:
                print("Warning: Unable to parse quantum estimation output for recording")

            return None
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to run Q# estimation: {e}")
            self.latest_quantum_result = None
            return None
        except FileNotFoundError:
            print("dotnet not found. Please install .NET SDK.")
            self.latest_quantum_result = None
            return None

    def ensure_classical_baseline(self) -> bool:
        """Ensure classical baseline results exist, generating them if needed."""
        classical_file = self.estimates_dir / "classical_baseline.json"
        if classical_file.exists():
            return True

        script_path = self.problem_dir / "python" / "classical_baseline.py"
        if not script_path.exists():
            print("Classical baseline script not found")
            return False

        try:
            print("Generating classical baseline...")
            subprocess.run(
                [sys.executable, str(script_path)],
                cwd=script_path.parent,
                check=True,
            )
            return classical_file.exists()
        except subprocess.CalledProcessError as e:
            print(f"Failed to generate classical baseline: {e}")
            return False
    
    def _compose_ensemble_payload(self, results: List[Dict[str, Any]], runs_requested: int) -> Dict[str, Any]:
        """Aggregate metrics across multiple quantum estimation results."""
        metrics_list = [res.get("metrics", {}) for res in results if isinstance(res.get("metrics"), dict)]

        def _collect_float(key: str) -> List[float]:
            collected: List[float] = []
            for metrics in metrics_list:
                value = metrics.get(key)
                if isinstance(value, (int, float)):
                    collected.append(float(value))
            return collected

        amplitude_values = _collect_float("quantum_estimate")
        std_error_values = _collect_float("quantum_std_error")
        difference_values = _collect_float("difference")
        circular_amp_values = _collect_float("circular_amplitude")
        circular_phase_values = _collect_float("circular_phase")

        amplitude_mean = statistics.mean(amplitude_values) if amplitude_values else None
        amplitude_std = statistics.pstdev(amplitude_values) if amplitude_values else None
        amplitude_std_error = None
        if amplitude_std is not None and amplitude_values:
            amplitude_std_error = amplitude_std / math.sqrt(len(amplitude_values)) if len(amplitude_values) > 0 else None

        std_error_mean = statistics.mean(std_error_values) if std_error_values else None
        difference_mean = statistics.mean(difference_values) if difference_values else None
        circular_amp_mean = statistics.mean(circular_amp_values) if circular_amp_values else None
        circular_phase_mean = statistics.mean(circular_phase_values) if circular_phase_values else None

        histogram_totals: Dict[int, int] = {}
        for res in results:
            for outcome, count in (res.get("histogram_counts") or {}).items():
                histogram_totals[outcome] = histogram_totals.get(outcome, 0) + count

        first_result = results[0]
        base_metrics = first_result.get("metrics", {})
        ensemble_metrics: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "algorithm": "QPEAmplitudeEstimation",
            "mode": "ensemble",
            "estimator_target": first_result.get("estimator_target", "TailRisk > 3.0"),
            "instance": first_result.get("instance", {}),
            "metrics": {
                "ensemble_runs": len(results),
                "runs_requested": runs_requested,
                "quantum_estimate": amplitude_mean,
                "ensemble_std_deviation": amplitude_std,
                "ensemble_std_error": amplitude_std_error,
                "mean_reported_std_error": std_error_mean,
                "mean_difference": difference_mean,
                "circular_amplitude": circular_amp_mean,
                "circular_phase": circular_phase_mean,
                "phase_bits": base_metrics.get("phase_bits"),
                "repetitions": base_metrics.get("repetitions"),
                "logical_qubits": base_metrics.get("logical_qubits"),
                "physical_qubits": base_metrics.get("physical_qubits"),
                "t_count": base_metrics.get("t_count"),
                "runtime_days": base_metrics.get("runtime_days"),
            },
            "ensemble": {
                "runs": [
                    {
                        "index": idx + 1,
                        "timestamp": res.get("timestamp"),
                        "metrics": res.get("metrics", {}),
                        "source_file": f"quantum_estimate_run{idx + 1}.json",
                    }
                    for idx, res in enumerate(results)
                ]
            },
        }

        ensemble_payload: Dict[str, Any] = ensemble_metrics

        if histogram_totals:
            ensemble_payload["histogram_counts"] = histogram_totals

        return ensemble_payload

    def run_quantum_ensemble(self, runs: int, qae_params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Execute multiple quantum estimations and aggregate the results."""
        if runs <= 0:
            print("Ensemble run count must be positive.")
            return None

        results: List[Dict[str, Any]] = []
        print(f"Running ensemble of {runs} quantum estimations...")
        for idx in range(runs):
            print(f"\n▶️ Ensemble run {idx + 1}/{runs}")
            result = self.run_quantum_estimation(skip_build=(idx > 0), qae_params=qae_params)
            if result is None:
                print("Ensemble execution aborted due to failure.")
                break

            results.append(result)
            run_path = self.estimates_dir / f"quantum_estimate_run{idx + 1}.json"
            with open(run_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
            print(f"Saved run {idx + 1} results to {run_path}")

        if not results:
            return None

        ensemble_payload = self._compose_ensemble_payload(results, runs)
        ensemble_path = self.estimates_dir / "quantum_estimate_ensemble.json"
        with open(ensemble_path, "w", encoding="utf-8") as f:
            json.dump(ensemble_payload, f, indent=2)
        print(f"Saved ensemble summary to {ensemble_path}")

        self.latest_quantum_result = ensemble_payload
        return ensemble_payload
            
    def create_resource_comparison_plot(self, estimation_results: List[Dict[str, Any]]):
        """Create plots comparing resource requirements across targets."""
        
        if not estimation_results:
            print("No estimation results to plot")
            return
            
        # Convert to DataFrame for easier plotting
        data = []
        for result in estimation_results:
            metrics = result.get('metrics', {})
            data.append({
                'Target': result.get('estimator_target', 'unknown'),
                'Logical Qubits': metrics.get('logical_qubits', 0),
                'Physical Qubits': metrics.get('physical_qubits', 0),
                'T-count': metrics.get('t_count', 0),
                'Runtime (days)': metrics.get('runtime_days', 0),
                'Algorithm': result.get('algorithm', 'unknown')
            })
            
        df = pd.DataFrame(data)

        numeric_cols = ['Logical Qubits', 'Physical Qubits', 'T-count', 'Runtime (days)']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        if df.empty:
            print("No valid data for plotting")
            return
            
        # Create subplot grid
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('QAE Resource Requirements Comparison', fontsize=16)
        
        # Logical qubits
        axes[0, 0].bar(df['Target'], df['Logical Qubits'], color='skyblue')
        axes[0, 0].set_title('Logical Qubits Required')
        axes[0, 0].set_ylabel('Count')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Physical qubits (log scale)
        axes[0, 1].bar(df['Target'], df['Physical Qubits'], color='lightcoral')
        axes[0, 1].set_title('Physical Qubits Required')
        axes[0, 1].set_ylabel('Count')
        self._apply_safe_log_scale(axes[0, 1], df['Physical Qubits'])
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # T-count (log scale)
        axes[1, 0].bar(df['Target'], df['T-count'], color='lightgreen')
        axes[1, 0].set_title('T Gate Count')
        axes[1, 0].set_ylabel('Count')
        self._apply_safe_log_scale(axes[1, 0], df['T-count'])
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Runtime
        axes[1, 1].bar(df['Target'], df['Runtime (days)'], color='gold')
        axes[1, 1].set_title('Estimated Runtime')
        axes[1, 1].set_ylabel('Days')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(self.plots_dir / "resource_comparison.png", dpi=300, bbox_inches='tight')
        if self.show_plots:
            plt.show()
        else:
            plt.close(fig)
        
    def create_precision_vs_resources_plot(self, estimation_results: List[Dict[str, Any]]):
        """Plot how resource requirements scale with precision."""
        
        # Group results by precision if available
        precision_data = []
        
        for result in estimation_results:
            instance = result.get('instance', {})
            params = instance.get('parameters', {})
            
            # Try to extract precision from various possible sources
            precision = params.get('precision', params.get('epsilon', 0.01))
            
            metrics = result.get('metrics', {})
            precision_data.append({
                'Precision': precision,
                'Logical Qubits': metrics.get('logical_qubits', 0),
                'T-count': metrics.get('t_count', 0),
                'Runtime (days)': metrics.get('runtime_days', 0)
            })
            
        if not precision_data:
            print("No precision data available for plotting")
            return
            
        df = pd.DataFrame(precision_data).sort_values('Precision')
        df['Precision'] = pd.to_numeric(df['Precision'], errors='coerce')
        df['Logical Qubits'] = pd.to_numeric(df['Logical Qubits'], errors='coerce').fillna(0)
        df['T-count'] = pd.to_numeric(df['T-count'], errors='coerce').fillna(0)
        df['Runtime (days)'] = pd.to_numeric(df['Runtime (days)'], errors='coerce').fillna(0)
        df = df.dropna(subset=['Precision'])
        df = df[df['Precision'] > 0]
        
        if df.empty:
            print("No valid precision entries available for plotting")
            return

        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle('Resource Scaling vs. Precision', fontsize=16)
        
        # Logical qubits vs precision
        axes[0].semilogx(df['Precision'], df['Logical Qubits'], 'bo-', linewidth=2, markersize=8)
        axes[0].set_xlabel('Precision (ε)')
        axes[0].set_ylabel('Logical Qubits')
        axes[0].set_title('Logical Qubits vs. Precision')
        axes[0].grid(True)
        
        # T-count vs precision (log-log when possible)
        t_positive = df['T-count'] > 0
        if t_positive.any():
            axes[1].loglog(df.loc[t_positive, 'Precision'], df.loc[t_positive, 'T-count'], 'ro-', linewidth=2, markersize=8)
            axes[1].set_ylabel('T-count')
        else:
            axes[1].plot(df['Precision'], df['T-count'], 'ro-', linewidth=2, markersize=8)
            axes[1].set_ylabel('T-count (linear)')
        axes[1].set_xlabel('Precision (ε)')
        axes[1].set_title('T-count vs. Precision')
        axes[1].grid(True)
        
        # Runtime vs precision
        runtime_positive = df['Runtime (days)'] > 0
        if runtime_positive.any():
            axes[2].loglog(df.loc[runtime_positive, 'Precision'], df.loc[runtime_positive, 'Runtime (days)'], 'go-', linewidth=2, markersize=8)
            axes[2].set_ylabel('Runtime (days)')
        else:
            axes[2].plot(df['Precision'], df['Runtime (days)'], 'go-', linewidth=2, markersize=8)
            axes[2].set_ylabel('Runtime (days) (linear)')
        axes[2].set_xlabel('Precision (ε)')
        axes[2].set_title('Runtime vs. Precision')
        axes[2].grid(True)
        
        plt.tight_layout()
        plt.savefig(self.plots_dir / "precision_scaling.png", dpi=300, bbox_inches='tight')
        if self.show_plots:
            plt.show()
        else:
            plt.close(fig)
        
    def create_quantum_classical_comparison(self, 
                                          estimation_results: List[Dict[str, Any]], 
                                          classical_results: Dict[str, Any]):
        """Create comprehensive quantum vs classical comparison."""
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Quantum vs Classical Risk Analysis Comparison', fontsize=16)
        
        # Sample complexity comparison
        precisions = [0.1, 0.05, 0.01, 0.005, 0.001]
        quantum_queries = [1.0 / eps for eps in precisions]  # O(1/ε) scaling
        classical_samples = [0.05 * 0.95 / (eps * eps) for eps in precisions]  # O(1/ε²) scaling
        
        axes[0, 0].loglog(precisions, classical_samples, 'bo-', label='Classical (Monte Carlo)', linewidth=2)
        axes[0, 0].loglog(precisions, quantum_queries, 'ro-', label='Quantum (QAE)', linewidth=2)
        axes[0, 0].set_xlabel('Target Precision (ε)')
        axes[0, 0].set_ylabel('Samples/Queries Needed')
        axes[0, 0].set_title('Sample Complexity')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Speedup factor
        speedup = np.array(classical_samples) / np.array(quantum_queries)
        axes[0, 1].semilogx(precisions, speedup, 'go-', linewidth=2, markersize=8)
        axes[0, 1].set_xlabel('Target Precision (ε)')
        axes[0, 1].set_ylabel('Speedup Factor')
        axes[0, 1].set_title('Theoretical Quantum Speedup')
        axes[0, 1].grid(True)
        
        # Resource requirements (if quantum data available)
        if estimation_results:
            logical_qubits = [result.get('metrics', {}).get('logical_qubits', 0) for result in estimation_results]
            targets = [result.get('estimator_target', f'Target {i}') for i, result in enumerate(estimation_results)]
            
            axes[1, 0].bar(targets, logical_qubits, color='purple', alpha=0.7)
            axes[1, 0].set_title('Quantum Resource Requirements')
            axes[1, 0].set_ylabel('Logical Qubits')
            axes[1, 0].tick_params(axis='x', rotation=45)
        else:
            axes[1, 0].text(0.5, 0.5, 'No quantum\nresults available', 
                           ha='center', va='center', transform=axes[1, 0].transAxes)
            axes[1, 0].set_title('Quantum Resource Requirements')
            
        # Error comparison (if classical data available)
        if classical_results:
            # Extract first threshold's data for plotting
            first_threshold = list(classical_results.keys())[0]
            threshold_data = classical_results[first_threshold]
            
            classical_precisions = threshold_data.get('target_precisions', [])
            classical_errors = threshold_data.get('errors', [])
            
            if classical_precisions and classical_errors:
                axes[1, 1].semilogx(classical_precisions, classical_errors, 'bo-', linewidth=2)
                axes[1, 1].set_xlabel('Target Precision (ε)')
                axes[1, 1].set_ylabel('Standard Error')
                axes[1, 1].set_title('Classical Estimation Error')
                axes[1, 1].grid(True)
            else:
                axes[1, 1].text(0.5, 0.5, 'No classical\nerror data available', 
                               ha='center', va='center', transform=axes[1, 1].transAxes)
        else:
            axes[1, 1].text(0.5, 0.5, 'No classical\nresults available', 
                           ha='center', va='center', transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('Classical Estimation Error')
            
        plt.tight_layout()
        plt.savefig(self.plots_dir / "quantum_classical_comparison.png", dpi=300, bbox_inches='tight')
        if self.show_plots:
            plt.show()
        else:
            plt.close(fig)
        
    def generate_summary_report(self, 
                              estimation_results: List[Dict[str, Any]], 
                              classical_results: Dict[str, Any]) -> str:
        """Generate a summary report of the analysis."""
        
        report = []
        report.append("# QAE Risk Analysis Summary Report")
        report.append(f"Generated: {pd.Timestamp.now()}")
        report.append("")
        
        # Quantum results summary
        report.append("## Quantum Amplitude Estimation Results")
        single_results = [
            result for result in estimation_results
            if not result.get('metrics', {}).get('ensemble_runs')
        ]
        ensemble_results = [
            result for result in estimation_results
            if result.get('metrics', {}).get('ensemble_runs')
        ]

        if single_results:
            def format_with_commas(value: Any) -> str:
                """Format numeric values with thousands separators when possible."""
                if value is None:
                    return "N/A"
                if isinstance(value, (int, float)):
                    return f"{value:,}"
                try:
                    numeric_value = float(value)
                except (TypeError, ValueError):
                    return str(value)
                else:
                    if numeric_value.is_integer():
                        return f"{int(numeric_value):,}"
                    return f"{numeric_value:,}"

            for i, result in enumerate(single_results):
                metrics = result.get('metrics', {})
                report.append(f"### Result {i+1}: {result.get('estimator_target', 'Unknown')}")
                report.append(f"- Algorithm: {result.get('algorithm', 'Unknown')}")
                report.append(f"- Logical Qubits: {metrics.get('logical_qubits', 'N/A')}")
                report.append(f"- Physical Qubits: {format_with_commas(metrics.get('physical_qubits', 'N/A'))}")
                report.append(f"- T-count: {format_with_commas(metrics.get('t_count', 'N/A'))}")
                circular_amp = metrics.get('circular_amplitude')
                circular_phase = metrics.get('circular_phase')
                if circular_amp is not None:
                    report.append(f"- Circular amplitude (phase-averaged): {circular_amp:.6f}")
                if circular_phase is not None:
                    report.append(f"- Circular phase estimate: {circular_phase:.6f}")
                report.append(f"- Runtime: {metrics.get('runtime_days', 'N/A')} days")
                report.append("")
        else:
            report.append("No individual quantum estimation results available.")
            report.append("")

        if ensemble_results:
            report.append("## Quantum Ensemble Aggregations")
            for i, result in enumerate(ensemble_results):
                metrics = result.get('metrics', {})
                report.append(f"### Ensemble {i+1}: {result.get('estimator_target', 'Unknown')}")
                runs_recorded = metrics.get('ensemble_runs')
                runs_requested = metrics.get('runs_requested')
                if runs_recorded is not None:
                    requested_text = f" (requested {runs_requested})" if runs_requested is not None else ""
                    report.append(f"- Completed runs: {runs_recorded}{requested_text}")
                mean_amp = metrics.get('quantum_estimate')
                if isinstance(mean_amp, (int, float)):
                    report.append(f"- Ensemble mean amplitude: {mean_amp:.6f}")
                std_dev = metrics.get('ensemble_std_deviation')
                if isinstance(std_dev, (int, float)):
                    report.append(f"- Ensemble standard deviation: {std_dev:.6f}")
                std_err = metrics.get('ensemble_std_error')
                if isinstance(std_err, (int, float)):
                    report.append(f"- Ensemble standard error: {std_err:.6f}")
                reported_err = metrics.get('mean_reported_std_error')
                if isinstance(reported_err, (int, float)):
                    report.append(f"- Mean per-run reported std. error: {reported_err:.6f}")
                diff_mean = metrics.get('mean_difference')
                if isinstance(diff_mean, (int, float)):
                    report.append(f"- Mean deviation from analytic: {diff_mean:.6f}")
                circ_amp = metrics.get('circular_amplitude')
                if isinstance(circ_amp, (int, float)):
                    report.append(f"- Circular amplitude (aggregated): {circ_amp:.6f}")
                circ_phase = metrics.get('circular_phase')
                if isinstance(circ_phase, (int, float)):
                    report.append(f"- Circular phase (aggregated): {circ_phase:.6f}")
                ensemble_hist = result.get('histogram_counts')
                if ensemble_hist:
                    peak_outcome = max(ensemble_hist.items(), key=lambda kv: kv[1])[0]
                    phase_bits = metrics.get('phase_bits')
                    if isinstance(phase_bits, int) and phase_bits >= 0:
                        denom = 1 << phase_bits
                        report.append(f"- Most frequent outcome across ensemble: {peak_outcome}/{denom}")
                    else:
                        report.append(f"- Most frequent outcome across ensemble: {peak_outcome} (denominator unknown)")
                runs_entries = result.get('ensemble', {}).get('runs')
                if runs_entries:
                    run_labels = [run.get('source_file', f"run{idx+1}") for idx, run in enumerate(runs_entries)]
                    if run_labels:
                        report.append(f"- Run artifacts: {', '.join(run_labels)}")
                report.append("")
            
        # Classical results summary
        report.append("## Classical Monte Carlo Results")
        if classical_results:
            for threshold, data in classical_results.items():
                report.append(f"### Threshold = {threshold}")
                precisions = data.get('target_precisions', [])
                samples = data.get('samples_needed', [])
                
                if precisions and samples:
                    report.append("| Precision | Samples Needed | Runtime |")
                    report.append("|-----------|----------------|---------|")
                    
                    runtimes = data.get('runtimes', [0] * len(precisions))
                    for p, s, r in zip(precisions, samples, runtimes):
                        report.append(f"| {p} | {s:,} | {r:.3f}s |")
                report.append("")
        else:
            report.append("No classical results available.")
            report.append("")
            
        # Comparison and conclusions
        report.append("## Analysis Conclusions")
        report.append("### Quantum Advantage")
        report.append("- **Theoretical**: Quadratic speedup for high-precision estimates")
        report.append("- **Practical**: Advantage emerges at ε < 0.001 precision levels")
        report.append("- **Current Status**: Requires fault-tolerant quantum computers")
        report.append("")
        
        report.append("### Key Insights")
        report.append("1. QAE provides quadratic speedup in precision requirements")
        report.append("2. Resource overhead is significant for near-term quantum devices")
        report.append("3. Classical methods remain competitive for moderate precision")
        report.append("4. Quantum advantage most pronounced for tail risk analysis")
        report.append("")
        
        report.append("### Next Steps")
        report.append("- Implement noise-aware QAE variants")
        report.append("- Optimize state preparation circuits")
        report.append("- Analyze real financial datasets")
        report.append("- Compare with advanced classical methods")
        
        report_text = "\n".join(report)
        
        # Save report
        with open(self.plots_dir / "analysis_report.md", 'w', encoding='utf-8') as f:
            f.write(report_text)
            
        return report_text

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze QAE risk estimation outputs")
    parser.add_argument("--show-plots", action="store_true", help="Display plots instead of just saving them")
    parser.add_argument(
        "--instance-file",
        default="../instances/small.yaml",
        help="Instance YAML to seed QAE runtime parameters (default: ../instances/small.yaml)",
    )
    parser.add_argument("--loss-qubits", type=int, default=None, help="Override loss encoding qubit count")
    parser.add_argument("--threshold", type=float, default=None, help="Override tail-risk threshold")
    parser.add_argument("--mean", type=float, default=None, help="Override log-normal mean")
    parser.add_argument("--std-dev", type=float, default=None, help="Override log-normal std dev")
    parser.add_argument("--precision-bits", type=int, default=None, help="Override QAE precision qubits")
    parser.add_argument("--repetitions", type=int, default=None, help="Override QAE repetition count")
    parser.add_argument(
        "--run-sanity-check",
        dest="run_sanity_check",
        action="store_true",
        help="Run the built-in QAE sanity test before risk analysis",
    )
    parser.add_argument(
        "--skip-sanity-check",
        dest="run_sanity_check",
        action="store_false",
        help="Skip the built-in QAE sanity test",
    )
    parser.set_defaults(run_sanity_check=None)
    parser.add_argument(
        "--ensemble-runs",
        type=int,
        default=1,
        help="Number of quantum estimation runs to perform for aggregation (default: 1)",
    )
    return parser.parse_args()


def _resolve_qae_parameters(problem_dir: Path, args: argparse.Namespace) -> Dict[str, Any]:
    resolved = dict(DEFAULT_QAE_PARAMS)

    instance_path = Path(args.instance_file)
    if not instance_path.is_absolute():
        instance_path = (problem_dir / "python" / instance_path).resolve()

    if instance_path.exists():
        with open(instance_path, "r", encoding="utf-8") as f:
            instance_data = yaml.safe_load(f) or {}

        loss_encoding = instance_data.get("loss_encoding", {})
        if isinstance(loss_encoding.get("num_qubits"), int):
            resolved["loss_qubits"] = int(loss_encoding["num_qubits"])

        if isinstance(instance_data.get("risk_threshold"), (int, float)):
            resolved["threshold"] = float(instance_data["risk_threshold"])

        amplitude_estimation = instance_data.get("amplitude_estimation", {})
        if isinstance(amplitude_estimation.get("precision_qubits"), int):
            resolved["precision_bits"] = int(amplitude_estimation["precision_qubits"])
        if isinstance(amplitude_estimation.get("repetitions"), int):
            resolved["repetitions"] = int(amplitude_estimation["repetitions"])

        distribution = instance_data.get("distribution", {})
        dist_type = str(distribution.get("type", "")).lower()
        dist_params = distribution.get("parameters", {}) if isinstance(distribution, dict) else {}
        if dist_type in ("log_normal", "", "none"):
            if isinstance(dist_params.get("mean"), (int, float)):
                resolved["mean"] = float(dist_params["mean"])
            if isinstance(dist_params.get("std_dev"), (int, float)):
                resolved["std_dev"] = float(dist_params["std_dev"])
        elif dist_type:
            print(
                f"Warning: Instance distribution type '{dist_type}' is not directly supported by current Q# model; "
                "retaining log-normal mean/std defaults unless explicitly overridden."
            )

    else:
        print(f"Warning: Instance file not found at {instance_path}; using built-in defaults.")

    if args.loss_qubits is not None:
        resolved["loss_qubits"] = args.loss_qubits
    if args.threshold is not None:
        resolved["threshold"] = args.threshold
    if args.mean is not None:
        resolved["mean"] = args.mean
    if args.std_dev is not None:
        resolved["std_dev"] = args.std_dev
    if args.precision_bits is not None:
        resolved["precision_bits"] = args.precision_bits
    if args.repetitions is not None:
        resolved["repetitions"] = args.repetitions
    if args.run_sanity_check is not None:
        resolved["run_sanity_check"] = bool(args.run_sanity_check)

    return resolved


def main(args: argparse.Namespace):
    """Main analysis workflow."""
    
    analyzer = QAERiskAnalyzer(show_plots=args.show_plots)
    qae_params = _resolve_qae_parameters(analyzer.problem_dir, args)
    
    print("🔍 Starting QAE Risk Analysis...")
    print(
        "QAE runtime params: "
        f"loss_qubits={qae_params['loss_qubits']}, "
        f"threshold={qae_params['threshold']}, "
        f"mean={qae_params['mean']}, "
        f"std_dev={qae_params['std_dev']}, "
        f"precision_bits={qae_params['precision_bits']}, "
        f"repetitions={qae_params['repetitions']}, "
        f"run_sanity_check={qae_params['run_sanity_check']}"
    )
    
    # Try to run quantum estimation
    ensemble_runs = max(1, args.ensemble_runs)
    if ensemble_runs > 1:
        print(f"\n📊 Running quantum estimation ensemble with {ensemble_runs} runs...")
        quantum_result = analyzer.run_quantum_ensemble(ensemble_runs, qae_params=qae_params)
        if quantum_result is None:
            print("Quantum ensemble execution failed or was skipped. See logs above.")
    else:
        print("\n📊 Running quantum estimation...")
        quantum_result = analyzer.run_quantum_estimation(qae_params=qae_params)
        if quantum_result is None:
            print("Quantum estimation failed or was skipped. See logs above.")
    
    # Load any existing results
    print("\n📁 Loading estimation results...")
    estimation_results = analyzer.load_estimation_results()
    print(f"Found {len(estimation_results)} estimation result(s)")
    
    # Load classical results
    print("\n📁 Loading classical baseline...")
    classical_results = analyzer.load_classical_results()
    if not classical_results:
        if analyzer.ensure_classical_baseline():
            classical_results = analyzer.load_classical_results()
    
    # Generate visualizations
    print("\n📈 Generating plots...")
    
    if estimation_results:
        analyzer.create_resource_comparison_plot(estimation_results)
        analyzer.create_precision_vs_resources_plot(estimation_results)
    
    analyzer.create_quantum_classical_comparison(estimation_results, classical_results)
    
    # Generate summary report
    print("\n📝 Generating summary report...")
    report = analyzer.generate_summary_report(estimation_results, classical_results)
    
    print("\n✅ Analysis complete!")
    print(f"📊 Plots saved to: {analyzer.plots_dir}")
    print(f"📄 Report saved to: {analyzer.plots_dir / 'analysis_report.md'}")
    
    # Print short summary
    print("\n=== SUMMARY ===")
    if estimation_results:
        latest = estimation_results[-1]
        metrics = latest.get('metrics', {})
        print(f"Latest quantum estimate: {metrics.get('logical_qubits', 'N/A')} logical qubits")
    
    if classical_results:
        print(f"Classical analysis complete for {len(classical_results)} threshold(s)")
    
    print("=================")

if __name__ == "__main__":
    # Set plotting style
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")

    args = parse_args()
    main(args)
