# Initiative: Solution Architecture + Pricing

Living tracker for the "after code-gen, draw the architecture and price the run" capability.
Improve this piece by piece as new quantum hardware ships and Azure best practices change.

## Goal

After the evaluator picks a platform (with high confidence) and the code generator
produces code + resource estimates, automatically:

1. **Draw the solution architecture** (Mermaid) grounded in the real recommendation
   (target quantum hardware + qubit count, or HPC/AI-ML VM SKUs).
2. **Guesstimate the run cost** of that specific solution using the pricing calculator,
   including the qubit-availability crossover (at what hardware width quantum becomes
   runnable / cheaper).

Example: "Simulate the ground state energy of a 50-atom lithium cobalt oxide battery
cathode material" at 88% confidence -> draw the Azure Quantum architecture, then price
a representative run and state when it becomes feasible on real hardware.

## Status (2026-06-15)

| Piece | State |
| --- | --- |
| Pricing calculator (cost_model + azure_pricing) | DONE, verified live |
| Qubit-availability crossover (`quantum_hardware_feasibility`) | DONE (baseline) |
| Architecture generator (deterministic Mermaid, grounded) | Increment 1 |
| Solution pricing (`price_solution`, uses real resource estimate) | Increment 1 |
| API wiring (`/api/evaluate` returns `architecture_diagram` + `solution_pricing`) | Increment 1 |
| Website rendering (Mermaid + pricing card) | Increment 1 |
| Agent + Microsoft Learn / Azure Architecture Center enrichment | Increment 2 (roadmap) |
| Per-hardware crossover table refresh as devices ship | Ongoing |

## Architecture: deterministic baseline first

Increment 1 uses deterministic, grounded Mermaid templates per platform
(`agents/code_generator/architecture.py`). This is reliable and testable and ties
directly to the resource estimate. The agent (Foundry, model-router) already has the
Microsoft Learn MCP tool; Increment 2 will let it enrich the diagram with Azure
Architecture Center reference patterns.

## Pricing: tied to the generated solution

`price_solution` (in `agents/classifier/cost_model.py`) prices the recommended
platform using the real code-gen `estimation` (physical_qubits, runtime_ns) rather
than KB defaults, and reports the qubit crossover from `quantum_hardware_feasibility`.

## Qubit-availability crossover

`azure_pricing.QUANTUM_HARDWARE_QUBITS` holds current device widths. As new hardware
ships (more qubits, better fidelity, lower per-shot price), update:

- `agents/classifier/azure_pricing.py`: `QUANTUM_HARDWARE_QUBITS` and per-provider rates
- `agents/classifier/cost_model.py`: `REPRESENTATIVE_NISQ_DEPTH` if coherence improves

The crossover answer ("feasible_today" + "needs N qubits, hardware has M") then updates
automatically.

## Roadmap / next increments

- **Increment 2**: agent-enriched architecture using Microsoft Learn MCP +
  Azure Architecture Center patterns (add an Azure MCP or a curated reference index).
- **Increment 3**: cost-vs-qubit-count curve (plot run cost as device width grows to the
  required scale) so the crossover point is visual.
- **Increment 4**: include data-loading (I/O) and error-correction overhead in the
  run-cost estimate, aligned with Troyer Part 6 once published.
- **Ongoing**: refresh `QUANTUM_HARDWARE_QUBITS` and provider rates per hardware release.

## Data sources to wire in

- Azure Retail Prices API (already used by `azure_pricing`).
- Azure Quantum pricing page (learn.microsoft.com/azure/quantum/pricing).
- Azure Architecture Center (via Microsoft Learn MCP) for reference architectures.
