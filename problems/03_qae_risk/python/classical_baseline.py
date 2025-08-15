#!/usr/bin/env python3
"""
Classical Monte Carlo baseline for QAE Risk Analysis.
Provides comparison baseline for quantum amplitude estimation results.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path
from scipy import stats
from typing import Tuple, Dict, Any
import time

class ClassicalRiskAnalysis:
    """Classical risk analysis using Monte Carlo simulation."""
    
    def __init__(self, mean: float = 0.0, std_dev: float = 1.0):
        """
        Initialize with log-normal distribution parameters.
        
        Args:
            mean: Mean of underlying normal distribution (log-space)
            std_dev: Standard deviation of underlying normal distribution
        """
        self.mean = mean
        self.std_dev = std_dev
        
    def sample_loss_distribution(self, n_samples: int) -> np.ndarray:
        """
        Sample from log-normal loss distribution.
        
        Args:
            n_samples: Number of samples to generate
            
        Returns:
            Array of loss values
        """
        # Sample from normal distribution first
        normal_samples = np.random.normal(self.mean, self.std_dev, n_samples)
        
        # Transform to log-normal
        loss_samples = np.exp(normal_samples)
        
        return loss_samples
        
    def estimate_tail_probability(self, 
                                threshold: float, 
                                n_samples: int = 100000) -> Tuple[float, float, float]:
        """
        Estimate P(Loss > threshold) using Monte Carlo.
        
        Args:
            threshold: Risk threshold value
            n_samples: Number of Monte Carlo samples
            
        Returns:
            Tuple of (probability_estimate, standard_error, runtime_seconds)
        """
        start_time = time.time()
        
        # Generate samples
        losses = self.sample_loss_distribution(n_samples)
        
        # Count tail events
        tail_events = np.sum(losses > threshold)
        
        # Calculate probability and standard error
        probability = tail_events / n_samples
        standard_error = np.sqrt(probability * (1 - probability) / n_samples)
        
        runtime = time.time() - start_time
        
        return probability, standard_error, runtime
        
    def run_precision_analysis(self, 
                             threshold: float,
                             target_precisions: list = [0.1, 0.05, 0.01, 0.005, 0.001]) -> Dict[str, Any]:
        """
        Analyze samples needed for different precision levels.
        
        Args:
            threshold: Risk threshold
            target_precisions: List of target precision levels (ε)
            
        Returns:
            Dictionary with precision analysis results
        """
        results = {
            'threshold': threshold,
            'target_precisions': target_precisions,
            'samples_needed': [],
            'runtimes': [],
            'estimates': [],
            'errors': []
        }
        
        for precision in target_precisions:
            # Theoretical samples needed: n ≈ p(1-p)/ε² where p ≈ 0.05 for tail risk
            theoretical_samples = int(0.05 * 0.95 / (precision * precision))
            
            # Use at least this many samples
            n_samples = max(theoretical_samples, 1000)
            
            prob, error, runtime = self.estimate_tail_probability(threshold, n_samples)
            
            results['samples_needed'].append(n_samples)
            results['runtimes'].append(runtime)
            results['estimates'].append(prob)
            results['errors'].append(error)
            
        return results
        
    def plot_distribution_and_threshold(self, threshold: float, save_path: str = None):
        """Plot the loss distribution with risk threshold marked."""
        
        # Generate samples for plotting
        samples = self.sample_loss_distribution(10000)
        
        # Create the plot
        plt.figure(figsize=(10, 6))
        
        # Plot histogram
        plt.hist(samples, bins=50, density=True, alpha=0.7, color='skyblue', 
                label='Loss Distribution')
        
        # Plot theoretical PDF
        x_range = np.linspace(0.1, np.percentile(samples, 99), 1000)
        theoretical_pdf = stats.lognorm.pdf(x_range, s=self.std_dev, scale=np.exp(self.mean))
        plt.plot(x_range, theoretical_pdf, 'r-', linewidth=2, label='Theoretical PDF')
        
        # Mark threshold
        plt.axvline(threshold, color='red', linestyle='--', linewidth=2, 
                   label=f'Risk Threshold = {threshold}')
        
        # Fill tail area
        tail_x = x_range[x_range > threshold]
        tail_y = stats.lognorm.pdf(tail_x, s=self.std_dev, scale=np.exp(self.mean))
        plt.fill_between(tail_x, tail_y, alpha=0.3, color='red', label='Tail Risk Region')
        
        plt.xlabel('Loss Value')
        plt.ylabel('Probability Density')
        plt.title('Loss Distribution with Risk Threshold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
    def plot_precision_comparison(self, results: Dict[str, Any], save_path: str = None):
        """Plot classical vs quantum precision requirements."""
        
        precisions = results['target_precisions']
        samples = results['samples_needed']
        
        # Theoretical quantum queries (linear in 1/ε)
        quantum_queries = [1.0 / eps for eps in precisions]
        
        plt.figure(figsize=(12, 8))
        
        # Subplot 1: Sample complexity
        plt.subplot(2, 2, 1)
        plt.loglog(precisions, samples, 'bo-', label='Classical (Monte Carlo)', linewidth=2)
        plt.loglog(precisions, quantum_queries, 'ro-', label='Quantum (QAE)', linewidth=2)
        plt.xlabel('Target Precision (ε)')
        plt.ylabel('Samples/Queries Needed')
        plt.title('Sample Complexity Comparison')
        plt.legend()
        plt.grid(True)
        
        # Subplot 2: Speedup factor
        plt.subplot(2, 2, 2)
        speedup = np.array(samples) / np.array(quantum_queries)
        plt.semilogx(precisions, speedup, 'go-', linewidth=2)
        plt.xlabel('Target Precision (ε)')
        plt.ylabel('Speedup Factor')
        plt.title('Theoretical Quantum Speedup')
        plt.grid(True)
        
        # Subplot 3: Runtime comparison
        plt.subplot(2, 2, 3)
        plt.loglog(precisions, results['runtimes'], 'bo-', label='Classical Runtime', linewidth=2)
        # Hypothetical quantum runtime (would need actual hardware)
        quantum_runtime = [q * 1e-6 for q in quantum_queries]  # Assume 1μs per query
        plt.loglog(precisions, quantum_runtime, 'ro-', label='Quantum Runtime (hypothetical)', linewidth=2)
        plt.xlabel('Target Precision (ε)')
        plt.ylabel('Runtime (seconds)')
        plt.title('Runtime Comparison')
        plt.legend()
        plt.grid(True)
        
        # Subplot 4: Error estimates
        plt.subplot(2, 2, 4)
        plt.semilogx(precisions, results['errors'], 'bo-', linewidth=2)
        plt.xlabel('Target Precision (ε)')
        plt.ylabel('Standard Error')
        plt.title('Classical Estimation Error')
        plt.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

def main():
    """Run classical risk analysis and generate comparison plots."""
    
    # Initialize classical analyzer
    analyzer = ClassicalRiskAnalysis(mean=0.0, std_dev=1.0)
    
    # Risk thresholds to analyze
    thresholds = [2.0, 3.0, 4.0]  # Roughly 95th, 99th, 99.9th percentiles
    
    results = {}
    
    for threshold in thresholds:
        print(f"\n=== Analyzing threshold = {threshold} ===")
        
        # Quick estimate
        prob, error, runtime = analyzer.estimate_tail_probability(threshold, 100000)
        print(f"Probability estimate: {prob:.6f} ± {error:.6f}")
        print(f"Runtime: {runtime:.3f} seconds")
        
        # Precision analysis
        precision_results = analyzer.run_precision_analysis(threshold)
        results[threshold] = precision_results
        
        # Generate plots
        plots_dir = Path("../plots")
        plots_dir.mkdir(exist_ok=True)
        
        analyzer.plot_distribution_and_threshold(
            threshold, 
            save_path=plots_dir / f"distribution_threshold_{threshold}.png"
        )
        
        analyzer.plot_precision_comparison(
            precision_results,
            save_path=plots_dir / f"precision_comparison_{threshold}.png"
        )
        
    # Save results
    results_dir = Path("../estimates")
    results_dir.mkdir(exist_ok=True)
    
    with open(results_dir / "classical_baseline.json", 'w') as f:
        # Convert numpy arrays to lists for JSON serialization
        serializable_results = {}
        for threshold, data in results.items():
            serializable_results[str(threshold)] = {
                k: (v.tolist() if isinstance(v, np.ndarray) else v)
                for k, v in data.items()
            }
        
        json.dump(serializable_results, f, indent=2)
    
    print(f"\nResults saved to {results_dir / 'classical_baseline.json'}")
    print(f"Plots saved to ../plots/")

if __name__ == "__main__":
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Set plotting style
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    
    main()
