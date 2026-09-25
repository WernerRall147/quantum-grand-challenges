globalThis.BLOCH_EVIDENCE = {
  "schema_version": "1.0",
  "kind": "qgc-bloch-evidence",
  "description": "Empirical computational-basis frequencies, not tomography. X, Y and phase are unknown. Marker (0, 0, z) is a diagonal-state display convention, not a reconstruction of the original state. Exploration is an independent user-created pure state, never run evidence.",
  "problems": [
    {
      "id": "01_hubbard",
      "title": "Hubbard",
      "stage": "C",
      "archived": false,
      "metadata_source": {
        "path": "docs/objective-kpis.json",
        "sha256": "6d3be90fbc17ee3b4e4cc2067057aeb2bb76963f3e6265fe9aba87011db094d8"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "d3eaabb1d843f66465cf28bad556ee936d0dbf073d15131b69144953e191d0a7"
        },
        "source_generated_utc": "2026-09-25T13:14:39.101620Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "HubbardQPEKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[Zero, Zero]",
            "count": 132
          },
          {
            "outcome": "[One, Zero]",
            "count": 37
          },
          {
            "outcome": "[One, One]",
            "count": 19
          },
          {
            "outcome": "[Zero, One]",
            "count": 12
          }
        ]
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation."
      ],
      "measurement_width": 2,
      "marginals": [
        {
          "status": "available",
          "reason": null,
          "bit": 0,
          "measurement_width": 2,
          "shots": 200,
          "counts": {
            "0": 144,
            "1": 56
          },
          "p0": 0.72,
          "p1": 0.28,
          "z": 0.44,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        },
        {
          "status": "available",
          "reason": null,
          "bit": 1,
          "measurement_width": 2,
          "shots": 200,
          "counts": {
            "0": 169,
            "1": 31
          },
          "p0": 0.845,
          "p1": 0.155,
          "z": 0.69,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        }
      ]
    },
    {
      "id": "02_catalysis",
      "title": "Catalysis",
      "stage": "C",
      "archived": false,
      "metadata_source": {
        "path": "docs/objective-kpis.json",
        "sha256": "6d3be90fbc17ee3b4e4cc2067057aeb2bb76963f3e6265fe9aba87011db094d8"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "d3eaabb1d843f66465cf28bad556ee936d0dbf073d15131b69144953e191d0a7"
        },
        "source_generated_utc": "2026-09-25T13:14:39.101620Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "CatalysisQPEKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[One, Zero]",
            "count": 181
          },
          {
            "outcome": "[Zero, Zero]",
            "count": 9
          },
          {
            "outcome": "[One, One]",
            "count": 5
          },
          {
            "outcome": "[Zero, One]",
            "count": 5
          }
        ]
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation."
      ],
      "measurement_width": 2,
      "marginals": [
        {
          "status": "available",
          "reason": null,
          "bit": 0,
          "measurement_width": 2,
          "shots": 200,
          "counts": {
            "0": 14,
            "1": 186
          },
          "p0": 0.07,
          "p1": 0.93,
          "z": -0.86,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        },
        {
          "status": "available",
          "reason": null,
          "bit": 1,
          "measurement_width": 2,
          "shots": 200,
          "counts": {
            "0": 190,
            "1": 10
          },
          "p0": 0.95,
          "p1": 0.05,
          "z": 0.9,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        }
      ]
    },
    {
      "id": "03_qae_risk",
      "title": "Qae Risk",
      "stage": "D",
      "archived": true,
      "metadata_source": {
        "path": "docs/objective-kpis.json",
        "sha256": "6d3be90fbc17ee3b4e4cc2067057aeb2bb76963f3e6265fe9aba87011db094d8"
      },
      "run": {
        "status": "missing",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "d3eaabb1d843f66465cf28bad556ee936d0dbf073d15131b69144953e191d0a7"
        },
        "source_generated_utc": "2026-09-25T13:14:39.101620Z",
        "execution": null,
        "target": null,
        "entry_point": null,
        "shots": null,
        "histogram": []
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation.",
        "No successful local-simulator histogram in the selected run source.",
        "Archived problem; not an active quantum-advantage candidate."
      ],
      "measurement_width": null,
      "marginals": [
        {
          "status": "unavailable",
          "reason": "No matching simulator run",
          "bit": 0,
          "measurement_width": null,
          "shots": null,
          "counts": null,
          "p0": null,
          "p1": null,
          "z": null,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        }
      ]
    },
    {
      "id": "04_linear_solvers",
      "title": "Linear Solvers",
      "stage": "B",
      "archived": true,
      "metadata_source": {
        "path": "docs/objective-kpis.json",
        "sha256": "6d3be90fbc17ee3b4e4cc2067057aeb2bb76963f3e6265fe9aba87011db094d8"
      },
      "run": {
        "status": "missing",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "d3eaabb1d843f66465cf28bad556ee936d0dbf073d15131b69144953e191d0a7"
        },
        "source_generated_utc": "2026-09-25T13:14:39.101620Z",
        "execution": null,
        "target": null,
        "entry_point": null,
        "shots": null,
        "histogram": []
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation.",
        "No successful local-simulator histogram in the selected run source.",
        "Archived problem; not an active quantum-advantage candidate."
      ],
      "measurement_width": null,
      "marginals": [
        {
          "status": "unavailable",
          "reason": "No matching simulator run",
          "bit": 0,
          "measurement_width": null,
          "shots": null,
          "counts": null,
          "p0": null,
          "p1": null,
          "z": null,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        }
      ]
    },
    {
      "id": "05_qaoa_maxcut",
      "title": "Qaoa Maxcut",
      "stage": "D",
      "archived": true,
      "metadata_source": {
        "path": "docs/objective-kpis.json",
        "sha256": "6d3be90fbc17ee3b4e4cc2067057aeb2bb76963f3e6265fe9aba87011db094d8"
      },
      "run": {
        "status": "missing",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "d3eaabb1d843f66465cf28bad556ee936d0dbf073d15131b69144953e191d0a7"
        },
        "source_generated_utc": "2026-09-25T13:14:39.101620Z",
        "execution": null,
        "target": null,
        "entry_point": null,
        "shots": null,
        "histogram": []
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation.",
        "No successful local-simulator histogram in the selected run source.",
        "Archived problem; not an active quantum-advantage candidate."
      ],
      "measurement_width": null,
      "marginals": [
        {
          "status": "unavailable",
          "reason": "No matching simulator run",
          "bit": 0,
          "measurement_width": null,
          "shots": null,
          "counts": null,
          "p0": null,
          "p1": null,
          "z": null,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        }
      ]
    },
    {
      "id": "06_high_frequency_trading",
      "title": "High Frequency Trading",
      "stage": "B",
      "archived": true,
      "metadata_source": {
        "path": "docs/objective-kpis.json",
        "sha256": "6d3be90fbc17ee3b4e4cc2067057aeb2bb76963f3e6265fe9aba87011db094d8"
      },
      "run": {
        "status": "missing",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "d3eaabb1d843f66465cf28bad556ee936d0dbf073d15131b69144953e191d0a7"
        },
        "source_generated_utc": "2026-09-25T13:14:39.101620Z",
        "execution": null,
        "target": null,
        "entry_point": null,
        "shots": null,
        "histogram": []
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation.",
        "No successful local-simulator histogram in the selected run source.",
        "Archived problem; not an active quantum-advantage candidate."
      ],
      "measurement_width": null,
      "marginals": [
        {
          "status": "unavailable",
          "reason": "No matching simulator run",
          "bit": 0,
          "measurement_width": null,
          "shots": null,
          "counts": null,
          "p0": null,
          "p1": null,
          "z": null,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        }
      ]
    },
    {
      "id": "07_drug_discovery",
      "title": "Drug Discovery",
      "stage": "C",
      "archived": false,
      "metadata_source": {
        "path": "docs/objective-kpis.json",
        "sha256": "6d3be90fbc17ee3b4e4cc2067057aeb2bb76963f3e6265fe9aba87011db094d8"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "d3eaabb1d843f66465cf28bad556ee936d0dbf073d15131b69144953e191d0a7"
        },
        "source_generated_utc": "2026-09-25T13:14:39.101620Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "DrugBindingQPEKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[One, Zero]",
            "count": 196
          },
          {
            "outcome": "[Zero, One]",
            "count": 2
          },
          {
            "outcome": "[Zero, Zero]",
            "count": 2
          }
        ]
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation."
      ],
      "measurement_width": 2,
      "marginals": [
        {
          "status": "available",
          "reason": null,
          "bit": 0,
          "measurement_width": 2,
          "shots": 200,
          "counts": {
            "0": 4,
            "1": 196
          },
          "p0": 0.02,
          "p1": 0.98,
          "z": -0.96,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        },
        {
          "status": "available",
          "reason": null,
          "bit": 1,
          "measurement_width": 2,
          "shots": 200,
          "counts": {
            "0": 198,
            "1": 2
          },
          "p0": 0.99,
          "p1": 0.01,
          "z": 0.98,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        }
      ]
    },
    {
      "id": "08_protein_folding",
      "title": "Protein Folding",
      "stage": "B",
      "archived": true,
      "metadata_source": {
        "path": "docs/objective-kpis.json",
        "sha256": "6d3be90fbc17ee3b4e4cc2067057aeb2bb76963f3e6265fe9aba87011db094d8"
      },
      "run": {
        "status": "missing",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "d3eaabb1d843f66465cf28bad556ee936d0dbf073d15131b69144953e191d0a7"
        },
        "source_generated_utc": "2026-09-25T13:14:39.101620Z",
        "execution": null,
        "target": null,
        "entry_point": null,
        "shots": null,
        "histogram": []
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation.",
        "No successful local-simulator histogram in the selected run source.",
        "Archived problem; not an active quantum-advantage candidate."
      ],
      "measurement_width": null,
      "marginals": [
        {
          "status": "unavailable",
          "reason": "No matching simulator run",
          "bit": 0,
          "measurement_width": null,
          "shots": null,
          "counts": null,
          "p0": null,
          "p1": null,
          "z": null,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        }
      ]
    },
    {
      "id": "09_factorization",
      "title": "Factorization",
      "stage": "C",
      "archived": false,
      "metadata_source": {
        "path": "docs/objective-kpis.json",
        "sha256": "6d3be90fbc17ee3b4e4cc2067057aeb2bb76963f3e6265fe9aba87011db094d8"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "d3eaabb1d843f66465cf28bad556ee936d0dbf073d15131b69144953e191d0a7"
        },
        "source_generated_utc": "2026-09-25T13:14:39.101620Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "ShorKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[Zero, Zero, Zero, Zero]",
            "count": 96
          },
          {
            "outcome": "[One, Zero, Zero, Zero]",
            "count": 41
          },
          {
            "outcome": "[One, One, One, One]",
            "count": 37
          },
          {
            "outcome": "[One, Zero, One, One]",
            "count": 9
          },
          {
            "outcome": "[One, One, Zero, Zero]",
            "count": 6
          },
          {
            "outcome": "[One, One, Zero, One]",
            "count": 5
          },
          {
            "outcome": "[One, Zero, One, Zero]",
            "count": 4
          },
          {
            "outcome": "[One, One, One, Zero]",
            "count": 2
          }
        ]
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation."
      ],
      "measurement_width": 4,
      "marginals": [
        {
          "status": "available",
          "reason": null,
          "bit": 0,
          "measurement_width": 4,
          "shots": 200,
          "counts": {
            "0": 96,
            "1": 104
          },
          "p0": 0.48,
          "p1": 0.52,
          "z": -0.04,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        },
        {
          "status": "available",
          "reason": null,
          "bit": 1,
          "measurement_width": 4,
          "shots": 200,
          "counts": {
            "0": 150,
            "1": 50
          },
          "p0": 0.75,
          "p1": 0.25,
          "z": 0.5,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        },
        {
          "status": "available",
          "reason": null,
          "bit": 2,
          "measurement_width": 4,
          "shots": 200,
          "counts": {
            "0": 148,
            "1": 52
          },
          "p0": 0.74,
          "p1": 0.26,
          "z": 0.48,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        },
        {
          "status": "available",
          "reason": null,
          "bit": 3,
          "measurement_width": 4,
          "shots": 200,
          "counts": {
            "0": 149,
            "1": 51
          },
          "p0": 0.745,
          "p1": 0.255,
          "z": 0.49,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        }
      ]
    },
    {
      "id": "10_post_quantum_cryptography",
      "title": "Post Quantum Cryptography",
      "stage": "B",
      "archived": true,
      "metadata_source": {
        "path": "docs/objective-kpis.json",
        "sha256": "6d3be90fbc17ee3b4e4cc2067057aeb2bb76963f3e6265fe9aba87011db094d8"
      },
      "run": {
        "status": "missing",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "d3eaabb1d843f66465cf28bad556ee936d0dbf073d15131b69144953e191d0a7"
        },
        "source_generated_utc": "2026-09-25T13:14:39.101620Z",
        "execution": null,
        "target": null,
        "entry_point": null,
        "shots": null,
        "histogram": []
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation.",
        "No successful local-simulator histogram in the selected run source.",
        "Archived problem; not an active quantum-advantage candidate."
      ],
      "measurement_width": null,
      "marginals": [
        {
          "status": "unavailable",
          "reason": "No matching simulator run",
          "bit": 0,
          "measurement_width": null,
          "shots": null,
          "counts": null,
          "p0": null,
          "p1": null,
          "z": null,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        }
      ]
    },
    {
      "id": "11_quantum_machine_learning",
      "title": "Quantum Machine Learning",
      "stage": "B",
      "archived": true,
      "metadata_source": {
        "path": "docs/objective-kpis.json",
        "sha256": "6d3be90fbc17ee3b4e4cc2067057aeb2bb76963f3e6265fe9aba87011db094d8"
      },
      "run": {
        "status": "missing",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "d3eaabb1d843f66465cf28bad556ee936d0dbf073d15131b69144953e191d0a7"
        },
        "source_generated_utc": "2026-09-25T13:14:39.101620Z",
        "execution": null,
        "target": null,
        "entry_point": null,
        "shots": null,
        "histogram": []
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation.",
        "No successful local-simulator histogram in the selected run source.",
        "Archived problem; not an active quantum-advantage candidate."
      ],
      "measurement_width": null,
      "marginals": [
        {
          "status": "unavailable",
          "reason": "No matching simulator run",
          "bit": 0,
          "measurement_width": null,
          "shots": null,
          "counts": null,
          "p0": null,
          "p1": null,
          "z": null,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        }
      ]
    },
    {
      "id": "12_quantum_optimization",
      "title": "Quantum Optimization",
      "stage": "B",
      "archived": true,
      "metadata_source": {
        "path": "docs/objective-kpis.json",
        "sha256": "6d3be90fbc17ee3b4e4cc2067057aeb2bb76963f3e6265fe9aba87011db094d8"
      },
      "run": {
        "status": "missing",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "d3eaabb1d843f66465cf28bad556ee936d0dbf073d15131b69144953e191d0a7"
        },
        "source_generated_utc": "2026-09-25T13:14:39.101620Z",
        "execution": null,
        "target": null,
        "entry_point": null,
        "shots": null,
        "histogram": []
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation.",
        "No successful local-simulator histogram in the selected run source.",
        "Archived problem; not an active quantum-advantage candidate."
      ],
      "measurement_width": null,
      "marginals": [
        {
          "status": "unavailable",
          "reason": "No matching simulator run",
          "bit": 0,
          "measurement_width": null,
          "shots": null,
          "counts": null,
          "p0": null,
          "p1": null,
          "z": null,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        }
      ]
    },
    {
      "id": "13_climate_modeling",
      "title": "Climate Modeling",
      "stage": "B",
      "archived": true,
      "metadata_source": {
        "path": "docs/objective-kpis.json",
        "sha256": "6d3be90fbc17ee3b4e4cc2067057aeb2bb76963f3e6265fe9aba87011db094d8"
      },
      "run": {
        "status": "missing",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "d3eaabb1d843f66465cf28bad556ee936d0dbf073d15131b69144953e191d0a7"
        },
        "source_generated_utc": "2026-09-25T13:14:39.101620Z",
        "execution": null,
        "target": null,
        "entry_point": null,
        "shots": null,
        "histogram": []
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation.",
        "No successful local-simulator histogram in the selected run source.",
        "Archived problem; not an active quantum-advantage candidate."
      ],
      "measurement_width": null,
      "marginals": [
        {
          "status": "unavailable",
          "reason": "No matching simulator run",
          "bit": 0,
          "measurement_width": null,
          "shots": null,
          "counts": null,
          "p0": null,
          "p1": null,
          "z": null,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        }
      ]
    },
    {
      "id": "14_materials_discovery",
      "title": "Materials Discovery",
      "stage": "C",
      "archived": false,
      "metadata_source": {
        "path": "docs/objective-kpis.json",
        "sha256": "6d3be90fbc17ee3b4e4cc2067057aeb2bb76963f3e6265fe9aba87011db094d8"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "d3eaabb1d843f66465cf28bad556ee936d0dbf073d15131b69144953e191d0a7"
        },
        "source_generated_utc": "2026-09-25T13:14:39.101620Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "MaterialsQPEKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[One, Zero]",
            "count": 114
          },
          {
            "outcome": "[Zero, Zero]",
            "count": 46
          },
          {
            "outcome": "[One, One]",
            "count": 29
          },
          {
            "outcome": "[Zero, One]",
            "count": 11
          }
        ]
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation."
      ],
      "measurement_width": 2,
      "marginals": [
        {
          "status": "available",
          "reason": null,
          "bit": 0,
          "measurement_width": 2,
          "shots": 200,
          "counts": {
            "0": 57,
            "1": 143
          },
          "p0": 0.285,
          "p1": 0.715,
          "z": -0.43,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        },
        {
          "status": "available",
          "reason": null,
          "bit": 1,
          "measurement_width": 2,
          "shots": 200,
          "counts": {
            "0": 160,
            "1": 40
          },
          "p0": 0.8,
          "p1": 0.2,
          "z": 0.6,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        }
      ]
    },
    {
      "id": "15_database_search",
      "title": "Database Search",
      "stage": "D",
      "archived": true,
      "metadata_source": {
        "path": "docs/objective-kpis.json",
        "sha256": "6d3be90fbc17ee3b4e4cc2067057aeb2bb76963f3e6265fe9aba87011db094d8"
      },
      "run": {
        "status": "missing",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "d3eaabb1d843f66465cf28bad556ee936d0dbf073d15131b69144953e191d0a7"
        },
        "source_generated_utc": "2026-09-25T13:14:39.101620Z",
        "execution": null,
        "target": null,
        "entry_point": null,
        "shots": null,
        "histogram": []
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation.",
        "No successful local-simulator histogram in the selected run source.",
        "Archived problem; not an active quantum-advantage candidate."
      ],
      "measurement_width": null,
      "marginals": [
        {
          "status": "unavailable",
          "reason": "No matching simulator run",
          "bit": 0,
          "measurement_width": null,
          "shots": null,
          "counts": null,
          "p0": null,
          "p1": null,
          "z": null,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        }
      ]
    },
    {
      "id": "16_error_correction",
      "title": "Error Correction",
      "stage": "C",
      "archived": false,
      "metadata_source": {
        "path": "docs/objective-kpis.json",
        "sha256": "6d3be90fbc17ee3b4e4cc2067057aeb2bb76963f3e6265fe9aba87011db094d8"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "d3eaabb1d843f66465cf28bad556ee936d0dbf073d15131b69144953e191d0a7"
        },
        "source_generated_utc": "2026-09-25T13:14:39.101620Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "QECKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[One]",
            "count": 103
          },
          {
            "outcome": "[Zero]",
            "count": 97
          }
        ]
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation."
      ],
      "measurement_width": 1,
      "marginals": [
        {
          "status": "available",
          "reason": null,
          "bit": 0,
          "measurement_width": 1,
          "shots": 200,
          "counts": {
            "0": 97,
            "1": 103
          },
          "p0": 0.485,
          "p1": 0.515,
          "z": -0.03,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        }
      ]
    },
    {
      "id": "17_nuclear_physics",
      "title": "Nuclear Physics",
      "stage": "C",
      "archived": false,
      "metadata_source": {
        "path": "docs/objective-kpis.json",
        "sha256": "6d3be90fbc17ee3b4e4cc2067057aeb2bb76963f3e6265fe9aba87011db094d8"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "d3eaabb1d843f66465cf28bad556ee936d0dbf073d15131b69144953e191d0a7"
        },
        "source_generated_utc": "2026-09-25T13:14:39.101620Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "NuclearQPEKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[One, Zero]",
            "count": 125
          },
          {
            "outcome": "[One, One]",
            "count": 35
          },
          {
            "outcome": "[Zero, Zero]",
            "count": 29
          },
          {
            "outcome": "[Zero, One]",
            "count": 11
          }
        ]
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation."
      ],
      "measurement_width": 2,
      "marginals": [
        {
          "status": "available",
          "reason": null,
          "bit": 0,
          "measurement_width": 2,
          "shots": 200,
          "counts": {
            "0": 40,
            "1": 160
          },
          "p0": 0.2,
          "p1": 0.8,
          "z": -0.6,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        },
        {
          "status": "available",
          "reason": null,
          "bit": 1,
          "measurement_width": 2,
          "shots": 200,
          "counts": {
            "0": 154,
            "1": 46
          },
          "p0": 0.77,
          "p1": 0.23,
          "z": 0.54,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        }
      ]
    },
    {
      "id": "18_photovoltaics",
      "title": "Photovoltaics",
      "stage": "C",
      "archived": false,
      "metadata_source": {
        "path": "docs/objective-kpis.json",
        "sha256": "6d3be90fbc17ee3b4e4cc2067057aeb2bb76963f3e6265fe9aba87011db094d8"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "d3eaabb1d843f66465cf28bad556ee936d0dbf073d15131b69144953e191d0a7"
        },
        "source_generated_utc": "2026-09-25T13:14:39.101620Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "QuantumWalkKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[One, Zero, Zero]",
            "count": 123
          },
          {
            "outcome": "[Zero, One, Zero]",
            "count": 37
          },
          {
            "outcome": "[Zero, Zero, Zero]",
            "count": 26
          },
          {
            "outcome": "[One, One, Zero]",
            "count": 14
          }
        ]
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation."
      ],
      "measurement_width": 3,
      "marginals": [
        {
          "status": "available",
          "reason": null,
          "bit": 0,
          "measurement_width": 3,
          "shots": 200,
          "counts": {
            "0": 63,
            "1": 137
          },
          "p0": 0.315,
          "p1": 0.685,
          "z": -0.37,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        },
        {
          "status": "available",
          "reason": null,
          "bit": 1,
          "measurement_width": 3,
          "shots": 200,
          "counts": {
            "0": 149,
            "1": 51
          },
          "p0": 0.745,
          "p1": 0.255,
          "z": 0.49,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        },
        {
          "status": "available",
          "reason": null,
          "bit": 2,
          "measurement_width": 3,
          "shots": 200,
          "counts": {
            "0": 200,
            "1": 0
          },
          "p0": 1.0,
          "p1": 0.0,
          "z": 1.0,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        }
      ]
    },
    {
      "id": "19_quantum_chromodynamics",
      "title": "Quantum Chromodynamics",
      "stage": "C",
      "archived": false,
      "metadata_source": {
        "path": "docs/objective-kpis.json",
        "sha256": "6d3be90fbc17ee3b4e4cc2067057aeb2bb76963f3e6265fe9aba87011db094d8"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "d3eaabb1d843f66465cf28bad556ee936d0dbf073d15131b69144953e191d0a7"
        },
        "source_generated_utc": "2026-09-25T13:14:39.101620Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "LatticeGaugeKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[Zero, Zero, Zero, Zero]",
            "count": 83
          },
          {
            "outcome": "[One, Zero, Zero, Zero]",
            "count": 28
          },
          {
            "outcome": "[Zero, Zero, Zero, One]",
            "count": 23
          },
          {
            "outcome": "[Zero, Zero, One, One]",
            "count": 18
          },
          {
            "outcome": "[One, One, Zero, Zero]",
            "count": 14
          },
          {
            "outcome": "[One, Zero, Zero, One]",
            "count": 11
          },
          {
            "outcome": "[One, One, One, One]",
            "count": 5
          },
          {
            "outcome": "[One, One, Zero, One]",
            "count": 5
          },
          {
            "outcome": "[Zero, One, One, Zero]",
            "count": 4
          },
          {
            "outcome": "[Zero, Zero, One, Zero]",
            "count": 3
          },
          {
            "outcome": "[One, Zero, One, One]",
            "count": 2
          },
          {
            "outcome": "[One, Zero, One, Zero]",
            "count": 2
          },
          {
            "outcome": "[Zero, One, One, One]",
            "count": 1
          },
          {
            "outcome": "[Zero, One, Zero, Zero]",
            "count": 1
          }
        ]
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation."
      ],
      "measurement_width": 4,
      "marginals": [
        {
          "status": "available",
          "reason": null,
          "bit": 0,
          "measurement_width": 4,
          "shots": 200,
          "counts": {
            "0": 133,
            "1": 67
          },
          "p0": 0.665,
          "p1": 0.335,
          "z": 0.33,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        },
        {
          "status": "available",
          "reason": null,
          "bit": 1,
          "measurement_width": 4,
          "shots": 200,
          "counts": {
            "0": 170,
            "1": 30
          },
          "p0": 0.85,
          "p1": 0.15,
          "z": 0.7,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        },
        {
          "status": "available",
          "reason": null,
          "bit": 2,
          "measurement_width": 4,
          "shots": 200,
          "counts": {
            "0": 165,
            "1": 35
          },
          "p0": 0.825,
          "p1": 0.175,
          "z": 0.65,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        },
        {
          "status": "available",
          "reason": null,
          "bit": 3,
          "measurement_width": 4,
          "shots": 200,
          "counts": {
            "0": 135,
            "1": 65
          },
          "p0": 0.675,
          "p1": 0.325,
          "z": 0.35,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        }
      ]
    },
    {
      "id": "20_space_mission_planning",
      "title": "Space Mission Planning",
      "stage": "B",
      "archived": true,
      "metadata_source": {
        "path": "docs/objective-kpis.json",
        "sha256": "6d3be90fbc17ee3b4e4cc2067057aeb2bb76963f3e6265fe9aba87011db094d8"
      },
      "run": {
        "status": "missing",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "d3eaabb1d843f66465cf28bad556ee936d0dbf073d15131b69144953e191d0a7"
        },
        "source_generated_utc": "2026-09-25T13:14:39.101620Z",
        "execution": null,
        "target": null,
        "entry_point": null,
        "shots": null,
        "histogram": []
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation.",
        "No successful local-simulator histogram in the selected run source.",
        "Archived problem; not an active quantum-advantage candidate."
      ],
      "measurement_width": null,
      "marginals": [
        {
          "status": "unavailable",
          "reason": "No matching simulator run",
          "bit": 0,
          "measurement_width": null,
          "shots": null,
          "counts": null,
          "p0": null,
          "p1": null,
          "z": null,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        }
      ]
    }
  ]
};
