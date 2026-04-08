{
  "tool_name": "qae_risk_analysis",
  "version_recommendation": "2026-tail-risk-update",
  "objectives": [
    "tail_probability",
    "value_at_risk",
    "conditional_value_at_risk",
    "expected_loss"
  ],
  "distribution_model": {
    "encoding_type": "discretized_loss_distribution",
    "loss_register_qubits": "n",
    "bins": "2^n",
    "state_preparation_operator": "A",
    "amplitude_target": "a = probability or bounded expectation of flagged bad outcomes",
    "notes": [
      "Track discretization error separately from estimator error",
      "Treat state preparation as a major bottleneck"
    ]
  },
  "quantum_estimators": {
    "default": "IQAE",
    "supported": [
      "IQAE",
      "MLAE",
      "FAE",
      "stabilized_ML_IQAE"
    ],
    "avoid_default": [
      "canonical_QPE_based_AE"
    ]
  },
  "iqae_params": {
    "epsilon_target": 0.01,
    "alpha": 0.05,
    "grover_power_schedule": "iterative/adaptive",
    "max_grover_iterations_hint": 16
  },
  "stabilized_ml_iqae_params": {
    "enable_interval_tracking": true,
    "enable_ml_inference": true,
    "enable_multi_hypothesis_feasibility_tracking": true,
    "enable_periodic_low_depth_disambiguation": true,
    "enable_bounded_restart": true,
    "failure_probability_budget": 0.05
  },
  "risk_metric_implementations": {
    "tail_probability": {
      "method": "threshold_oracle + amplitude_estimation"
    },
    "var": {
      "method": "bisection_search_over_thresholds",
      "max_search_steps": "n"
    },
    "cvar": {
      "method": "bounded_expectation_reformulation + amplitude_estimation"
    }
  },
  "benchmarking": {
    "primary_metric": "rmse_vs_query_budget",
    "secondary_metrics": [
      "bias",
      "variance",
      "confidence_interval_coverage",
      "tail_quantile_error"
    ],
    "classical_baselines_required": [
      "plain_monte_carlo",
      "variance_reduced_monte_carlo",
      "quasi_monte_carlo_if_applicable"
    ],
    "comparison_rule": "Use matched discretized oracle-model comparisons before claiming quantum advantage"
  },
  "complexity_targets": {
    "qae_target": "O(M^-1)",
    "mc_target": "O(M^-1/2)"
  },
  "production_guardrails": {
    "do_not_claim_advantage_if": [
      "classical baseline exploits closed-form structure unavailable to oracle-model QAE comparison",
      "discretization error dominates estimator error",
      "confidence/failure budget not reported"
    ],
    "report_separately": [
      "discretization_error",
      "state_preparation_cost",
      "oracle_query_count",
      "shot_count",
      "classical_runtime",
      "quantum_circuit_depth"
    ]
  },
  "recommended_outputs": {
    "always_return": [
      "estimated_metric",
      "confidence_interval",
      "oracle_queries",
      "shots",
      "discretization_summary",
      "baseline_comparison"
    ],
    "for_var_cvar": [
      "threshold_grid",
      "tail_probability_curve",
      "quantile_search_trace"
    ]
  }
}