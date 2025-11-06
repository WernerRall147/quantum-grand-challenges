"""
Quantum Algorithm Resource Comparison Visualizations

Generates comprehensive comparison plots for VQE, HHL, and QAE algorithms.
Run this script to create visualization dashboard for the quantum grand challenges.

Usage:
    python generate_comparison_plots.py
    
Output:
    - plots/qubit_comparison.png
    - plots/runtime_comparison.png
    - plots/tstate_comparison.png
    - plots/scaling_analysis.png
    - plots/quantum_advantage_map.png
"""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11

# Create output directory
output_dir = Path("plots")
output_dir.mkdir(exist_ok=True)

# Algorithm data
algorithms = ['VQE\n(Hubbard)', 'HHL\n(Linear Solver)', 'QAE\n(Risk Analysis)']
colors = ['#2E86AB', '#A23B72', '#F18F01']

# Resource data
physical_qubits = [79_250, 18_700, 594_000]  # Mean for VQE range
runtime_us = [114.5, 52_000, 6_400_000]  # Convert to microseconds
t_states = [1_596, 185_000, 965_000]
logical_qubits = [13, 6, 13]
t_factories = [2, 13, 17]

def create_qubit_comparison():
    """Create physical qubit comparison chart"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Bar chart
    bars = ax1.bar(algorithms, [q/1000 for q in physical_qubits], color=colors, alpha=0.8)
    ax1.set_ylabel('Physical Qubits (thousands)', fontsize=12, fontweight='bold')
    ax1.set_title('Physical Qubit Requirements', fontsize=14, fontweight='bold')
    ax1.set_ylim([0, 650])
    
    # Add value labels
    for bar, val in zip(bars, physical_qubits):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 20,
                f'{val/1000:.1f}k',
                ha='center', va='bottom', fontweight='bold')
    
    # Add relative comparison
    baseline = physical_qubits[1]  # HHL as baseline
    for i, (bar, val) in enumerate(zip(bars, physical_qubits)):
        if i != 1:
            ratio = val / baseline
            ax1.text(bar.get_x() + bar.get_width()/2., height/2,
                    f'{ratio:.1f}×\nHHL',
                    ha='center', va='center', fontsize=10, 
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Pie chart showing qubit allocation (using QAE as example)
    labels = ['T Factories\n(95.4%)', 'Algorithm\n(4.6%)']
    sizes = [95.4, 4.6]
    colors_pie = ['#F18F01', '#A8DADC']
    
    ax2.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%',
            startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
    ax2.set_title('QAE Qubit Allocation\n(T-factories dominate)', 
                  fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'qubit_comparison.png', dpi=300, bbox_inches='tight')
    print(f"✓ Created {output_dir / 'qubit_comparison.png'}")
    plt.close()

def create_runtime_comparison():
    """Create runtime comparison on log scale"""
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Log scale bar chart
    x_pos = np.arange(len(algorithms))
    bars = ax.bar(x_pos, runtime_us, color=colors, alpha=0.8, log=True)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(algorithms)
    ax.set_ylabel('Runtime (microseconds, log scale)', fontsize=12, fontweight='bold')
    ax.set_title('Algorithm Runtime Comparison', fontsize=14, fontweight='bold')
    ax.set_ylim([10, 10_000_000])
    
    # Add value labels with units
    units = ['114.5 μs', '52 ms', '6.4 s']
    for bar, val, unit in zip(bars, runtime_us, units):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height * 2,
                unit,
                ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    # Add speedup annotations
    ax.annotate('', xy=(1, runtime_us[1]), xytext=(0, runtime_us[0]),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax.text(0.5, np.sqrt(runtime_us[0] * runtime_us[1]), '454×\nslower',
            ha='center', va='center', fontsize=10, color='red', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    
    ax.annotate('', xy=(2, runtime_us[2]), xytext=(1, runtime_us[1]),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax.text(1.5, np.sqrt(runtime_us[1] * runtime_us[2]), '123×\nslower',
            ha='center', va='center', fontsize=10, color='red', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'runtime_comparison.png', dpi=300, bbox_inches='tight')
    print(f"✓ Created {output_dir / 'runtime_comparison.png'}")
    plt.close()

def create_tstate_comparison():
    """Create T-state comparison with breakdown"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Total T-states bar chart (log scale)
    bars = ax1.bar(algorithms, [t/1000 for t in t_states], color=colors, alpha=0.8)
    ax1.set_ylabel('Total T-States (thousands)', fontsize=12, fontweight='bold')
    ax1.set_title('T-State Requirements', fontsize=14, fontweight='bold')
    ax1.set_yscale('log')
    ax1.set_ylim([1, 2000])
    
    # Add value labels
    for bar, val in zip(bars, t_states):
        height = bar.get_height()
        label = f'{val/1000:.0f}k' if val >= 1000 else f'{val}'
        ax1.text(bar.get_x() + bar.get_width()/2., height * 1.3,
                label,
                ha='center', va='bottom', fontweight='bold')
    
    # T-state breakdown stacked bar chart
    # VQE: T-gates=18, Rotations=240, CCZ=0
    # HHL: T-gates=903, Rotations=244,800, CCZ=0
    # QAE: T-gates=240, Rotations=738,000, CCZ=227,280
    
    t_gates = np.array([18, 903, 240])
    rotations = np.array([240, 244_800, 738_000])
    ccz_gates = np.array([0, 0, 227_280])
    
    x_pos = np.arange(len(algorithms))
    width = 0.6
    
    p1 = ax2.bar(x_pos, t_gates/1000, width, label='T Gates', color='#457B9D', alpha=0.9)
    p2 = ax2.bar(x_pos, rotations/1000, width, bottom=t_gates/1000, 
                 label='Rotations (×20)', color='#F1FAEE', alpha=0.9)
    p3 = ax2.bar(x_pos, ccz_gates/1000, width, 
                 bottom=(t_gates + rotations)/1000,
                 label='CCZ Gates (×4)', color='#E63946', alpha=0.9)
    
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(algorithms)
    ax2.set_ylabel('T-States (thousands)', fontsize=12, fontweight='bold')
    ax2.set_title('T-State Breakdown by Source', fontsize=14, fontweight='bold')
    ax2.legend(loc='upper left', fontsize=10)
    ax2.set_ylim([0, 1000])
    
    plt.tight_layout()
    plt.savefig(output_dir / 'tstate_comparison.png', dpi=300, bbox_inches='tight')
    print(f"✓ Created {output_dir / 'tstate_comparison.png'}")
    plt.close()

def create_scaling_analysis():
    """Create scaling prediction charts"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # VQE scaling (Hubbard sites)
    sites = np.array([2, 10, 20, 50])
    vqe_qubits = 5000 * sites  # Approximate: 5k qubits per site
    vqe_runtime = 25 * sites  # μs
    
    ax1.plot(sites, vqe_qubits/1000, 'o-', color=colors[0], linewidth=2, markersize=8)
    ax1.set_xlabel('Number of Sites', fontweight='bold')
    ax1.set_ylabel('Physical Qubits (thousands)', fontweight='bold')
    ax1.set_title('VQE Scaling (Hubbard Model)', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([0, 300])
    
    # HHL scaling (system size N)
    N = np.array([4, 16, 64, 256, 1024])
    hhl_qubits = 5000 * np.log2(N)
    hhl_runtime = 13 * np.log2(N)  # ms (assuming κ=1)
    
    ax2.semilogx(N, hhl_qubits/1000, 's-', color=colors[1], linewidth=2, markersize=8)
    ax2.set_xlabel('System Size N', fontweight='bold')
    ax2.set_ylabel('Physical Qubits (thousands)', fontweight='bold')
    ax2.set_title('HHL Scaling (Linear Systems)', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim([0, 80])
    
    # QAE scaling (loss qubits)
    loss_qubits = np.array([4, 8, 12, 16])
    qae_qubits = 20_000 * 2**(loss_qubits/4)
    qae_runtime = 0.4 * 2**(loss_qubits/4)  # seconds
    
    ax3.semilogy(loss_qubits, qae_qubits/1000, '^-', color=colors[2], linewidth=2, markersize=8)
    ax3.set_xlabel('Loss Qubits', fontweight='bold')
    ax3.set_ylabel('Physical Qubits (thousands, log)', fontweight='bold')
    ax3.set_title('QAE Scaling (Risk Analysis)', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim([100, 100_000])
    
    # Combined runtime scaling
    ax4.semilogy(sites[:3], vqe_runtime[:3]/1000, 'o-', color=colors[0], 
                 linewidth=2, markersize=8, label='VQE (sites)')
    ax4.semilogy([4, 16, 64], hhl_runtime[:3], 's-', color=colors[1], 
                 linewidth=2, markersize=8, label='HHL (N=4,16,64)')
    ax4.semilogy(loss_qubits, qae_runtime*1000, '^-', color=colors[2], 
                 linewidth=2, markersize=8, label='QAE (loss qubits)')
    
    ax4.set_xlabel('Problem Size Parameter', fontweight='bold')
    ax4.set_ylabel('Runtime (ms, log scale)', fontweight='bold')
    ax4.set_title('Runtime Scaling Comparison', fontsize=12, fontweight='bold')
    ax4.legend(loc='upper left', fontsize=9)
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim([0.01, 10_000])
    
    plt.tight_layout()
    plt.savefig(output_dir / 'scaling_analysis.png', dpi=300, bbox_inches='tight')
    print(f"✓ Created {output_dir / 'scaling_analysis.png'}")
    plt.close()

def create_quantum_advantage_map():
    """Create quantum advantage assessment heatmap"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Define advantage criteria
    criteria = [
        'Qubit Efficiency',
        'Runtime Speed',
        'Error Tolerance',
        'Near-term Viability\n(2027-2029)',
        'Scalability',
        'Classical Advantage\nThreshold'
    ]
    
    # Scoring: 1-5 scale (5 = best)
    scores = np.array([
        [3, 5, 3],  # Qubit efficiency: VQE medium, HHL best, QAE worst
        [5, 3, 1],  # Runtime: VQE fastest, HHL medium, QAE slowest
        [5, 2, 2],  # Error tolerance: VQE high, HHL/QAE low
        [2, 5, 1],  # Near-term: HHL ready first, VQE soon, QAE distant
        [3, 4, 2],  # Scalability: HHL scales well, VQE good, QAE exponential
        [3, 4, 5],  # Advantage: VQE medium, HHL good, QAE strong (when large)
    ])
    
    # Create heatmap
    im = ax.imshow(scores, cmap='RdYlGn', aspect='auto', vmin=1, vmax=5)
    
    # Set ticks and labels
    ax.set_xticks(np.arange(len(algorithms)))
    ax.set_yticks(np.arange(len(criteria)))
    ax.set_xticklabels(algorithms, fontsize=11, fontweight='bold')
    ax.set_yticklabels(criteria, fontsize=11, fontweight='bold')
    
    # Add score annotations
    for i in range(len(criteria)):
        for j in range(len(algorithms)):
            score_text = ['Poor', 'Fair', 'Good', 'Very Good', 'Excellent'][scores[i, j]-1]
            text = ax.text(j, i, f'{scores[i, j]}\n{score_text}',
                          ha="center", va="center", color="black", 
                          fontsize=9, fontweight='bold')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, orientation='horizontal', pad=0.1, aspect=30)
    cbar.set_label('Score (1=Poor, 5=Excellent)', fontsize=11, fontweight='bold')
    cbar.set_ticks([1, 2, 3, 4, 5])
    cbar.set_ticklabels(['Poor', 'Fair', 'Good', 'Very Good', 'Excellent'])
    
    ax.set_title('Quantum Algorithm Advantage Assessment', 
                 fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'quantum_advantage_map.png', dpi=300, bbox_inches='tight')
    print(f"✓ Created {output_dir / 'quantum_advantage_map.png'}")
    plt.close()

def create_timeline_chart():
    """Create technology timeline chart"""
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Timeline data
    years = [2025, 2027, 2030, 2033, 2035]
    milestones = [
        'NISQ Era\n~1k qubits',
        'HHL Ready\n~50k qubits',
        'VQE Ready\n~100k qubits',
        'QAE Ready\n~1M qubits',
        'Full FT-QC\n~10M qubits'
    ]
    
    # Create timeline
    ax.plot(years, [0]*len(years), 'o-', color='#457B9D', markersize=15, linewidth=3)
    
    # Add milestone labels
    for year, milestone, offset in zip(years, milestones, [1, -1, 1, -1, 1]):
        ax.text(year, offset*0.3, milestone, ha='center', va='bottom' if offset > 0 else 'top',
                fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.7))
    
    # Add algorithm availability windows
    ax.axvspan(2027, 2029, alpha=0.2, color=colors[1], label='HHL Practical')
    ax.axvspan(2028, 2030, alpha=0.2, color=colors[0], label='VQE Practical')
    ax.axvspan(2033, 2035, alpha=0.2, color=colors[2], label='QAE Practical')
    
    ax.set_xlim([2024, 2036])
    ax.set_ylim([-0.8, 0.8])
    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_title('Quantum Computing Technology Roadmap', fontsize=14, fontweight='bold')
    ax.legend(loc='lower right', fontsize=10)
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.grid(True, axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'technology_timeline.png', dpi=300, bbox_inches='tight')
    print(f"✓ Created {output_dir / 'technology_timeline.png'}")
    plt.close()

def main():
    """Generate all comparison visualizations"""
    print("\n" + "="*60)
    print("Quantum Algorithm Comparison Visualization Generator")
    print("="*60 + "\n")
    
    print("Generating visualizations...")
    print()
    
    create_qubit_comparison()
    create_runtime_comparison()
    create_tstate_comparison()
    create_scaling_analysis()
    create_quantum_advantage_map()
    create_timeline_chart()
    
    print()
    print("="*60)
    print(f"✓ All visualizations saved to {output_dir}/")
    print("="*60)
    print()
    print("Generated plots:")
    print("  1. qubit_comparison.png - Physical qubit requirements")
    print("  2. runtime_comparison.png - Algorithm runtime comparison")
    print("  3. tstate_comparison.png - T-state requirements & breakdown")
    print("  4. scaling_analysis.png - Scaling predictions for each algorithm")
    print("  5. quantum_advantage_map.png - Advantage assessment heatmap")
    print("  6. technology_timeline.png - Practical deployment timeline")
    print()

if __name__ == "__main__":
    main()
