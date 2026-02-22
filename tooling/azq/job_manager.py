#!/usr/bin/env python3
"""
Azure Quantum job management utilities for Quantum Grand Challenges.
Simplifies submission, monitoring, and result retrieval.
"""

import json
import subprocess
import time
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

class AzureQuantumManager:
    """Wrapper for Azure Quantum CLI operations."""
    
    def __init__(self, workspace: str, resource_group: str, location: str = "eastus", cli_timeout_seconds: int = 120):
        self.workspace = workspace
        self.resource_group = resource_group
        self.location = location
        self.cli_timeout_seconds = cli_timeout_seconds
        
    def list_targets(self) -> List[Dict[str, Any]]:
        """List available quantum computing targets."""
        cmd = [
            "az", "quantum", "target", "list",
            "--workspace-name", self.workspace,
            "--resource-group", self.resource_group,
            "--output", "json"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=self.cli_timeout_seconds
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Failed to list targets: {e.stderr}", file=sys.stderr)
            return []
        except subprocess.TimeoutExpired:
            print("Failed to list targets: Azure CLI call timed out.", file=sys.stderr)
            return []
            
    def submit_job(self, 
                   qs_file: Path, 
                   target_id: str,
                   job_name: Optional[str] = None,
                   shots: int = 100,
                   parameters: Optional[Dict] = None,
                   job_input_format: str = "qir.v1",
                   entry_point: Optional[str] = None) -> Optional[str]:
        """
        Submit a Q# job to Azure Quantum.
        
        Args:
            qs_file: Path to compiled job input file (for example QIR bitcode)
            target_id: Target quantum computer ID
            job_name: Optional job name (auto-generated if None)
            shots: Number of shots to run
            parameters: Optional job parameters
            job_input_format: Azure Quantum input format identifier (for example qir.v1)
            entry_point: Optional QIR entry point (for example ENTRYPOINT__main)
            
        Returns:
            Job ID if successful, None otherwise
        """
        if job_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            job_name = f"qgc_{qs_file.stem}_{timestamp}"
            
        cmd = [
            "az", "quantum", "job", "submit",
            "--workspace-name", self.workspace,
            "--resource-group", self.resource_group,
            "--location", self.location,
            "--target-id", target_id,
            "--job-name", job_name,
            "--shots", str(shots),
            "--job-input-file", str(qs_file),
            "--job-input-format", job_input_format,
            "--output", "json"
        ]
        
        # Add parameters if provided
        if parameters:
            params_json = json.dumps(parameters)
            cmd.extend(["--job-params", params_json])

        if entry_point:
            cmd.extend(["--entry-point", entry_point])
            
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=self.cli_timeout_seconds
            )
            job_info = json.loads(result.stdout)
            job_id = job_info.get("id")
            print(f"Job submitted successfully: {job_id}")
            return job_id
        except subprocess.CalledProcessError as e:
            print(f"Failed to submit job: {e.stderr}", file=sys.stderr)
            return None
        except subprocess.TimeoutExpired:
            print("Failed to submit job: Azure CLI call timed out.", file=sys.stderr)
            return None
            
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status and details of a submitted job."""
        cmd = [
            "az", "quantum", "job", "show",
            "--workspace-name", self.workspace,
            "--resource-group", self.resource_group,
            "--job-id", job_id,
            "--output", "json"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=self.cli_timeout_seconds
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Failed to get job status: {e.stderr}", file=sys.stderr)
            return None
        except subprocess.TimeoutExpired:
            print("Failed to get job status: Azure CLI call timed out.", file=sys.stderr)
            return None
            
    def wait_for_completion(self, job_id: str, timeout_seconds: int = 3600) -> Optional[Dict[str, Any]]:
        """
        Wait for job completion and return final status.
        
        Args:
            job_id: Job identifier
            timeout_seconds: Maximum time to wait
            
        Returns:
            Final job status or None if timeout/error
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            status = self.get_job_status(job_id)
            if not status:
                return None
                
            job_status = status.get("status", "").lower()
            
            if job_status in ["succeeded", "failed", "cancelled"]:
                return status
            elif job_status == "waiting":
                print(f"Job {job_id} waiting in queue...")
            elif job_status == "executing":
                print(f"Job {job_id} executing...")
            else:
                print(f"Job {job_id} status: {job_status}")
                
            time.sleep(30)  # Check every 30 seconds
            
        print(f"Job {job_id} timed out after {timeout_seconds} seconds")
        return None
        
    def get_job_output(self, job_id: str, output_file: Optional[Path] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve job output/results.
        
        Args:
            job_id: Job identifier
            output_file: Optional file to save results
            
        Returns:
            Job results dictionary
        """
        cmd = [
            "az", "quantum", "job", "output",
            "--workspace-name", self.workspace,
            "--resource-group", self.resource_group,
            "--job-id", job_id,
            "--output", "json"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=self.cli_timeout_seconds
            )
            output = json.loads(result.stdout)
            
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump(output, f, indent=2)
                    
            return output
        except subprocess.CalledProcessError as e:
            print(f"Failed to get job output: {e.stderr}", file=sys.stderr)
            return None
        except subprocess.TimeoutExpired:
            print("Failed to get job output: Azure CLI call timed out.", file=sys.stderr)
            return None
            
    def run_job_complete(self, 
                        qs_file: Path,
                        target_id: str,
                        output_dir: Path,
                        shots: int = 100,
                        timeout_seconds: int = 3600,
                        job_input_format: str = "qir.v1",
                        entry_point: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Complete job workflow: submit, wait, retrieve results.
        
        Args:
            qs_file: Q# program to run
            target_id: Target quantum computer
            output_dir: Directory to save results
            shots: Number of shots
            timeout_seconds: Maximum wait time
            job_input_format: Azure Quantum input format identifier
            entry_point: Optional QIR entry point
            
        Returns:
            Combined job info and results
        """
        # Submit job
        job_id = self.submit_job(
            qs_file,
            target_id,
            shots=shots,
            job_input_format=job_input_format,
            entry_point=entry_point
        )
        if not job_id:
            return None

        # Ensure output directory exists before writing result artifacts.
        output_dir.mkdir(parents=True, exist_ok=True)
            
        # Wait for completion
        final_status = self.wait_for_completion(job_id, timeout_seconds)
        if not final_status:
            return None
            
        # Get results if successful
        if final_status.get("status", "").lower() == "succeeded":
            output_file = output_dir / f"job_{job_id}_results.json"
            results = self.get_job_output(job_id, output_file)
            
            # Combine status and results
            combined = {
                "job_id": job_id,
                "status": final_status,
                "results": results,
                "submission_time": datetime.utcnow().isoformat() + "Z"
            }
            
            # Save combined output
            combined_file = output_dir / f"job_{job_id}_complete.json"
            with open(combined_file, 'w') as f:
                json.dump(combined, f, indent=2)
                
            return combined
        else:
            print(f"Job {job_id} failed with status: {final_status.get('status')}")
            return final_status

def main():
    """CLI interface for Azure Quantum job management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage Azure Quantum jobs")
    parser.add_argument("--workspace", required=True, help="Azure Quantum workspace name")
    parser.add_argument("--resource-group", required=True, help="Azure resource group")
    parser.add_argument("--location", default="eastus", help="Azure location")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List targets command
    list_parser = subparsers.add_parser("list-targets", help="List available quantum targets")
    
    # Submit job command
    submit_parser = subparsers.add_parser("submit", help="Submit a job input file")
    submit_parser.add_argument("qs_file", help="Path to compiled job input file (for example QIR bitcode)")
    submit_parser.add_argument("--target", required=True, help="Target quantum computer ID")
    submit_parser.add_argument("--shots", type=int, default=100, help="Number of shots")
    submit_parser.add_argument("--name", help="Job name")
    submit_parser.add_argument("--input-format", default="qir.v1", help="Azure Quantum job input format")
    submit_parser.add_argument("--entry-point", help="Optional QIR entry point")
    
    # Check status command
    status_parser = subparsers.add_parser("status", help="Check job status")
    status_parser.add_argument("job_id", help="Job ID to check")
    
    # Get output command
    output_parser = subparsers.add_parser("output", help="Get job output")
    output_parser.add_argument("job_id", help="Job ID")
    output_parser.add_argument("--save", help="File to save output")
    
    # Run complete workflow
    run_parser = subparsers.add_parser("run", help="Submit job input and wait for results")
    run_parser.add_argument("qs_file", help="Path to compiled job input file (for example QIR bitcode)")
    run_parser.add_argument("--target", required=True, help="Target quantum computer ID")
    run_parser.add_argument("--output-dir", required=True, help="Directory to save results")
    run_parser.add_argument("--shots", type=int, default=100, help="Number of shots")
    run_parser.add_argument("--timeout", type=int, default=3600, help="Timeout in seconds")
    run_parser.add_argument("--input-format", default="qir.v1", help="Azure Quantum job input format")
    run_parser.add_argument("--entry-point", help="Optional QIR entry point")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    manager = AzureQuantumManager(args.workspace, args.resource_group, args.location)
    
    if args.command == "list-targets":
        targets = manager.list_targets()
        print(json.dumps(targets, indent=2))
        
    elif args.command == "submit":
        job_id = manager.submit_job(
            Path(args.qs_file), 
            args.target, 
            job_name=args.name,
            shots=args.shots,
            job_input_format=args.input_format,
            entry_point=args.entry_point
        )
        if job_id:
            print(f"Job ID: {job_id}")
            
    elif args.command == "status":
        status = manager.get_job_status(args.job_id)
        if status:
            print(json.dumps(status, indent=2))
            
    elif args.command == "output":
        output_file = Path(args.save) if args.save else None
        output = manager.get_job_output(args.job_id, output_file)
        if output and not args.save:
            print(json.dumps(output, indent=2))
            
    elif args.command == "run":
        result = manager.run_job_complete(
            Path(args.qs_file),
            args.target,
            Path(args.output_dir),
            shots=args.shots,
            timeout_seconds=args.timeout,
            job_input_format=args.input_format,
            entry_point=args.entry_point
        )
        if result:
            print(f"Job completed: {result['job_id']}")

if __name__ == "__main__":
    main()
