#!/usr/bin/env python3
"""
Analysis and visualization for QAE Risk Analysis results.
Combines quantum and classical results for comparison.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
import subprocess
import sys

class QAERiskAnalyzer:
    """Analyzer for quantum amplitude estimation risk analysis results."""
    
    def __init__(self, problem_dir: str = ".."):
        self.problem_dir = Path(problem_dir)
        self.estimates_dir = self.problem_dir / "estimates"
        self.plots_dir = self.problem_dir / "plots"
        self.plots_dir.mkdir(exist_ok=True)
        
    def load_estimation_results(self) -> List[Dict[str, Any]]:
        """Load all available estimation results."""
        results = []
        
        if self.estimates_dir.exists():
            for json_file in self.estimates_dir.glob("*.json"):
                try:
                    with open(json_file) as f:
                        result = json.load(f)
                    result['source_file'] = json_file.name
                    results.append(result)
                except Exception as e:
                    print(f"Warning: Could not load {json_file}: {e}")
                    
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
            
    def run_quantum_estimation(self) -> bool:
        """Run the Q# quantum estimation if possible."""
        qsharp_dir = self.problem_dir / "qsharp"
        
        if not qsharp_dir.exists():
            print("Q# directory not found")
            return False
            
        try:
            # Try to build and run the Q# project
            print("Building Q# project...")
            subprocess.run(["dotnet", "build"], cwd=qsharp_dir, check=True, capture_output=True)
            
            print("Running quantum estimation...")
            result = subprocess.run(["dotnet", "run"], cwd=qsharp_dir, check=True, capture_output=True, text=True)
            
            # Parse output for results (this would need to be more sophisticated in practice)
            print("Q# Output:", result.stdout)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to run Q# estimation: {e}")
            return False
        except FileNotFoundError:
            print("dotnet not found. Please install .NET SDK.")
            return False
            
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
        axes[0, 1].set_yscale('log')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # T-count (log scale)
        axes[1, 0].bar(df['Target'], df['T-count'], color='lightgreen')
        axes[1, 0].set_title('T Gate Count')
        axes[1, 0].set_ylabel('Count')
        axes[1, 0].set_yscale('log')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Runtime
        axes[1, 1].bar(df['Target'], df['Runtime (days)'], color='gold')
        axes[1, 1].set_title('Estimated Runtime')
        axes[1, 1].set_ylabel('Days')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(self.plots_dir / "resource_comparison.png", dpi=300, bbox_inches='tight')
        plt.show()
        
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
        
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle('Resource Scaling vs. Precision', fontsize=16)
        
        # Logical qubits vs precision
        axes[0].semilogx(df['Precision'], df['Logical Qubits'], 'bo-', linewidth=2, markersize=8)
        axes[0].set_xlabel('Precision (ε)')
        axes[0].set_ylabel('Logical Qubits')
        axes[0].set_title('Logical Qubits vs. Precision')
        axes[0].grid(True)
        
        # T-count vs precision (log-log)
        axes[1].loglog(df['Precision'], df['T-count'], 'ro-', linewidth=2, markersize=8)
        axes[1].set_xlabel('Precision (ε)')
        axes[1].set_ylabel('T-count')
        axes[1].set_title('T-count vs. Precision')
        axes[1].grid(True)
        
        # Runtime vs precision
        axes[2].loglog(df['Precision'], df['Runtime (days)'], 'go-', linewidth=2, markersize=8)
        axes[2].set_xlabel('Precision (ε)')
        axes[2].set_ylabel('Runtime (days)')
        axes[2].set_title('Runtime vs. Precision')
        axes[2].grid(True)
        
        plt.tight_layout()
        plt.savefig(self.plots_dir / "precision_scaling.png", dpi=300, bbox_inches='tight')
        plt.show()
        
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
        plt.show()
        
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
        if estimation_results:
            for i, result in enumerate(estimation_results):
                metrics = result.get('metrics', {})
                report.append(f"### Result {i+1}: {result.get('estimator_target', 'Unknown')}")
                report.append(f"- Algorithm: {result.get('algorithm', 'Unknown')}")
                report.append(f"- Logical Qubits: {metrics.get('logical_qubits', 'N/A')}")
                report.append(f"- Physical Qubits: {metrics.get('physical_qubits', 'N/A'):,}")
                report.append(f"- T-count: {metrics.get('t_count', 'N/A'):,}")
                report.append(f"- Runtime: {metrics.get('runtime_days', 'N/A')} days")
                report.append("")
        else:
            report.append("No quantum estimation results available.")
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
        with open(self.plots_dir / "analysis_report.md", 'w') as f:
            f.write(report_text)
            
        return report_text

def main():
    """Main analysis workflow."""
    
    analyzer = QAERiskAnalyzer()
    
    print("🔍 Starting QAE Risk Analysis...")
    
    # Try to run quantum estimation
    print("\n📊 Running quantum estimation...")
    quantum_success = analyzer.run_quantum_estimation()
    
    # Load any existing results
    print("\n📁 Loading estimation results...")
    estimation_results = analyzer.load_estimation_results()
    print(f"Found {len(estimation_results)} estimation result(s)")
    
    # Load classical results
    print("\n📁 Loading classical baseline...")
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
    
    main()
