#!/usr/bin/env python3
"""
Resource Estimator automation for Quantum Grand Challenges.
Runs Azure Quantum Resource Estimator with standardized targets and outputs.
"""

import json
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

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

class ResourceEstimator:
    """Wrapper for Azure Quantum Resource Estimator."""
    
    def __init__(self, problem_dir: Path):
        self.problem_dir = Path(problem_dir)
        self.estimates_dir = self.problem_dir / "estimates"
        self.estimates_dir.mkdir(exist_ok=True)
        
    def run_estimation(self, 
                      target_name: str,
                      qs_file: Optional[Path] = None,
                      instance_params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Run resource estimation for a given target.
        
        Args:
            target_name: Name of estimator target profile
            qs_file: Path to Q# file (defaults to qsharp/Program.qs)
            instance_params: Problem instance parameters
            
        Returns:
            Parsed estimation results
        """
        if target_name not in ESTIMATOR_TARGETS:
            raise ValueError(f"Unknown target: {target_name}")
            
        if qs_file is None:
            qs_file = self.problem_dir / "qsharp" / "Program.qs"
            
        if not qs_file.exists():
            raise FileNotFoundError(f"Q# file not found: {qs_file}")
            
        # Prepare estimation command
        cmd = [
            "qsharp-re",  # Resource Estimator CLI
            "--input", str(qs_file),
            "--target", target_name,
            "--output", "json"
        ]
        
        # Add instance parameters if provided
        if instance_params:
            params_file = self.estimates_dir / "temp_params.json"
            with open(params_file, 'w') as f:
                json.dump(instance_params, f)
            cmd.extend(["--params", str(params_file)])
            
        try:
            # Run estimation
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            raw_output = json.loads(result.stdout)
            
            # Transform to our standard schema
            standardized = self._standardize_output(raw_output, target_name, instance_params)
            
            # Save results
            timestamp = datetime.utcnow().isoformat() + "Z"
            output_file = self.estimates_dir / f"{target_name}_{timestamp.replace(':', '')}.json"
            
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
            if instance_params:
                params_file.unlink(missing_ok=True)
                
    def _standardize_output(self, raw_output: Dict, target_name: str, instance_params: Optional[Dict]) -> Dict[str, Any]:
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
            "algorithm": "unknown",  # Should be filled by caller
            "instance": {
                "description": f"Default instance for {problem_id}",
                "parameters": instance_params or {}
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
    import argparse
    
    parser = argparse.ArgumentParser(description="Run resource estimation for quantum problems")
    parser.add_argument("problem_dir", help="Path to problem directory")
    parser.add_argument("--target", default="surface_code_generic_v1", 
                       choices=list(ESTIMATOR_TARGETS.keys()),
                       help="Estimator target profile")
    parser.add_argument("--sweep", action="store_true",
                       help="Run parameter sweep across all targets")
    parser.add_argument("--params", help="JSON file with instance parameters")
    
    args = parser.parse_args()
    
    estimator = ResourceEstimator(args.problem_dir)
    
    # Load instance parameters if provided
    instance_params = None
    if args.params:
        with open(args.params) as f:
            instance_params = json.load(f)
            
    if args.sweep:
        # Run basic sweep across all targets
        results = estimator.run_parameter_sweep(
            list(ESTIMATOR_TARGETS.keys()),
            {"precision": [0.1, 0.01, 0.001]}
        )
        print(f"Completed parameter sweep: {len(results)} estimations")
    else:
        # Single estimation
        result = estimator.run_estimation(args.target, instance_params=instance_params)
        print(f"Estimation complete: {result['metrics']['logical_qubits']} logical qubits")

if __name__ == "__main__":
    main()
