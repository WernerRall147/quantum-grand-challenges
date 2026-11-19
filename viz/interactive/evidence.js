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
        "sha256": "4d82a9744ec6cffe35d3881c5127385b660e5378a74932b2692db5ea407fa5c9"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "cddf7aee2b726d1acf5792a5c5253e563c15241defe829579ce20ec99572f53d"
        },
        "source_generated_utc": "2026-11-19T12:29:23.371326Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "HubbardQPEKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[Zero, Zero]",
            "count": 131
          },
          {
            "outcome": "[One, Zero]",
            "count": 41
          },
          {
            "outcome": "[One, One]",
            "count": 18
          },
          {
            "outcome": "[Zero, One]",
            "count": 10
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
            "0": 141,
            "1": 59
          },
          "p0": 0.705,
          "p1": 0.295,
          "z": 0.41,
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
            "0": 172,
            "1": 28
          },
          "p0": 0.86,
          "p1": 0.14,
          "z": 0.72,
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
        "sha256": "4d82a9744ec6cffe35d3881c5127385b660e5378a74932b2692db5ea407fa5c9"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "cddf7aee2b726d1acf5792a5c5253e563c15241defe829579ce20ec99572f53d"
        },
        "source_generated_utc": "2026-11-19T12:29:23.371326Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "CatalysisQPEKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[One, Zero]",
            "count": 183
          },
          {
            "outcome": "[Zero, Zero]",
            "count": 7
          },
          {
            "outcome": "[One, One]",
            "count": 6
          },
          {
            "outcome": "[Zero, One]",
            "count": 4
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
            "0": 11,
            "1": 189
          },
          "p0": 0.055,
          "p1": 0.945,
          "z": -0.89,
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
        "sha256": "4d82a9744ec6cffe35d3881c5127385b660e5378a74932b2692db5ea407fa5c9"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "cddf7aee2b726d1acf5792a5c5253e563c15241defe829579ce20ec99572f53d"
        },
        "source_generated_utc": "2026-11-19T12:29:23.371326Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "QAEKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[One, One]",
            "count": 69
          },
          {
            "outcome": "[Zero, One]",
            "count": 66
          },
          {
            "outcome": "[Zero, Zero]",
            "count": 51
          },
          {
            "outcome": "[One, Zero]",
            "count": 14
          }
        ]
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation.",
        "Archived problem; not an active quantum-advantage candidate."
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
            "0": 117,
            "1": 83
          },
          "p0": 0.585,
          "p1": 0.415,
          "z": 0.17,
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
            "0": 65,
            "1": 135
          },
          "p0": 0.325,
          "p1": 0.675,
          "z": -0.35,
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
        "sha256": "4d82a9744ec6cffe35d3881c5127385b660e5378a74932b2692db5ea407fa5c9"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "cddf7aee2b726d1acf5792a5c5253e563c15241defe829579ce20ec99572f53d"
        },
        "source_generated_utc": "2026-11-19T12:29:23.371326Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "HHLKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[Zero, Zero]",
            "count": 111
          },
          {
            "outcome": "[Zero, One]",
            "count": 54
          },
          {
            "outcome": "[One, One]",
            "count": 20
          },
          {
            "outcome": "[One, Zero]",
            "count": 15
          }
        ]
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation.",
        "Archived problem; not an active quantum-advantage candidate."
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
          "bit": 1,
          "measurement_width": 2,
          "shots": 200,
          "counts": {
            "0": 126,
            "1": 74
          },
          "p0": 0.63,
          "p1": 0.37,
          "z": 0.26,
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
        "sha256": "4d82a9744ec6cffe35d3881c5127385b660e5378a74932b2692db5ea407fa5c9"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "cddf7aee2b726d1acf5792a5c5253e563c15241defe829579ce20ec99572f53d"
        },
        "source_generated_utc": "2026-11-19T12:29:23.371326Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "QaoaMaxCutKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[One, Zero, Zero]",
            "count": 39
          },
          {
            "outcome": "[Zero, One, One]",
            "count": 36
          },
          {
            "outcome": "[One, Zero, One]",
            "count": 35
          },
          {
            "outcome": "[Zero, One, Zero]",
            "count": 31
          },
          {
            "outcome": "[Zero, Zero, One]",
            "count": 31
          },
          {
            "outcome": "[One, One, Zero]",
            "count": 28
          }
        ]
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation.",
        "Archived problem; not an active quantum-advantage candidate."
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
            "0": 98,
            "1": 102
          },
          "p0": 0.49,
          "p1": 0.51,
          "z": -0.02,
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
            "0": 105,
            "1": 95
          },
          "p0": 0.525,
          "p1": 0.475,
          "z": 0.05,
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
            "0": 98,
            "1": 102
          },
          "p0": 0.49,
          "p1": 0.51,
          "z": -0.02,
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
        "sha256": "4d82a9744ec6cffe35d3881c5127385b660e5378a74932b2692db5ea407fa5c9"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "cddf7aee2b726d1acf5792a5c5253e563c15241defe829579ce20ec99572f53d"
        },
        "source_generated_utc": "2026-11-19T12:29:23.371326Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "HFTKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[One]",
            "count": 164
          },
          {
            "outcome": "[Zero]",
            "count": 36
          }
        ]
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation.",
        "Archived problem; not an active quantum-advantage candidate."
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
            "0": 36,
            "1": 164
          },
          "p0": 0.18,
          "p1": 0.82,
          "z": -0.64,
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
        "sha256": "4d82a9744ec6cffe35d3881c5127385b660e5378a74932b2692db5ea407fa5c9"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "cddf7aee2b726d1acf5792a5c5253e563c15241defe829579ce20ec99572f53d"
        },
        "source_generated_utc": "2026-11-19T12:29:23.371326Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "DrugBindingQPEKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[One, Zero]",
            "count": 191
          },
          {
            "outcome": "[One, One]",
            "count": 3
          },
          {
            "outcome": "[Zero, One]",
            "count": 3
          },
          {
            "outcome": "[Zero, Zero]",
            "count": 3
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
            "0": 6,
            "1": 194
          },
          "p0": 0.03,
          "p1": 0.97,
          "z": -0.94,
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
            "0": 194,
            "1": 6
          },
          "p0": 0.97,
          "p1": 0.03,
          "z": 0.94,
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
        "sha256": "4d82a9744ec6cffe35d3881c5127385b660e5378a74932b2692db5ea407fa5c9"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "cddf7aee2b726d1acf5792a5c5253e563c15241defe829579ce20ec99572f53d"
        },
        "source_generated_utc": "2026-11-19T12:29:23.371326Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "FoldingQaoaKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[Zero, Zero, Zero, Zero]",
            "count": 63
          },
          {
            "outcome": "[One, One, One, One]",
            "count": 58
          },
          {
            "outcome": "[Zero, Zero, One, One]",
            "count": 33
          },
          {
            "outcome": "[One, One, Zero, Zero]",
            "count": 17
          },
          {
            "outcome": "[Zero, One, One, One]",
            "count": 12
          },
          {
            "outcome": "[One, Zero, Zero, Zero]",
            "count": 6
          },
          {
            "outcome": "[One, One, One, Zero]",
            "count": 5
          },
          {
            "outcome": "[Zero, Zero, Zero, One]",
            "count": 3
          },
          {
            "outcome": "[Zero, One, One, Zero]",
            "count": 2
          },
          {
            "outcome": "[Zero, One, Zero, One]",
            "count": 1
          }
        ]
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation.",
        "Archived problem; not an active quantum-advantage candidate."
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
            "0": 114,
            "1": 86
          },
          "p0": 0.57,
          "p1": 0.43,
          "z": 0.14,
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
            "0": 105,
            "1": 95
          },
          "p0": 0.525,
          "p1": 0.475,
          "z": 0.05,
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
            "0": 90,
            "1": 110
          },
          "p0": 0.45,
          "p1": 0.55,
          "z": -0.1,
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
            "0": 93,
            "1": 107
          },
          "p0": 0.465,
          "p1": 0.535,
          "z": -0.07,
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
        "sha256": "4d82a9744ec6cffe35d3881c5127385b660e5378a74932b2692db5ea407fa5c9"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "cddf7aee2b726d1acf5792a5c5253e563c15241defe829579ce20ec99572f53d"
        },
        "source_generated_utc": "2026-11-19T12:29:23.371326Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "ShorKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[Zero, Zero, One, Zero]",
            "count": 65
          },
          {
            "outcome": "[Zero, Zero, One, One]",
            "count": 55
          },
          {
            "outcome": "[Zero, Zero, Zero, One]",
            "count": 41
          },
          {
            "outcome": "[Zero, Zero, Zero, Zero]",
            "count": 39
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
            "0": 200,
            "1": 0
          },
          "p0": 1.0,
          "p1": 0.0,
          "z": 1.0,
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
            "0": 200,
            "1": 0
          },
          "p0": 1.0,
          "p1": 0.0,
          "z": 1.0,
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
            "0": 80,
            "1": 120
          },
          "p0": 0.4,
          "p1": 0.6,
          "z": -0.2,
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
            "0": 104,
            "1": 96
          },
          "p0": 0.52,
          "p1": 0.48,
          "z": 0.04,
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
        "sha256": "4d82a9744ec6cffe35d3881c5127385b660e5378a74932b2692db5ea407fa5c9"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "cddf7aee2b726d1acf5792a5c5253e563c15241defe829579ce20ec99572f53d"
        },
        "source_generated_utc": "2026-11-19T12:29:23.371326Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "GroverKeyKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[One, Zero, One]",
            "count": 156
          },
          {
            "outcome": "[Zero, One, Zero]",
            "count": 11
          },
          {
            "outcome": "[Zero, One, One]",
            "count": 8
          },
          {
            "outcome": "[Zero, Zero, One]",
            "count": 8
          },
          {
            "outcome": "[One, One, Zero]",
            "count": 6
          },
          {
            "outcome": "[One, One, One]",
            "count": 5
          },
          {
            "outcome": "[One, Zero, Zero]",
            "count": 3
          },
          {
            "outcome": "[Zero, Zero, Zero]",
            "count": 3
          }
        ]
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation.",
        "Archived problem; not an active quantum-advantage candidate."
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
            "0": 30,
            "1": 170
          },
          "p0": 0.15,
          "p1": 0.85,
          "z": -0.7,
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
          "measurement_width": 3,
          "shots": 200,
          "counts": {
            "0": 23,
            "1": 177
          },
          "p0": 0.115,
          "p1": 0.885,
          "z": -0.77,
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
        "sha256": "4d82a9744ec6cffe35d3881c5127385b660e5378a74932b2692db5ea407fa5c9"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "cddf7aee2b726d1acf5792a5c5253e563c15241defe829579ce20ec99572f53d"
        },
        "source_generated_utc": "2026-11-19T12:29:23.371326Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "SwapTestKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[Zero]",
            "count": 186
          },
          {
            "outcome": "[One]",
            "count": 14
          }
        ]
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation.",
        "Archived problem; not an active quantum-advantage candidate."
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
            "0": 186,
            "1": 14
          },
          "p0": 0.93,
          "p1": 0.07,
          "z": 0.86,
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
        "sha256": "4d82a9744ec6cffe35d3881c5127385b660e5378a74932b2692db5ea407fa5c9"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "cddf7aee2b726d1acf5792a5c5253e563c15241defe829579ce20ec99572f53d"
        },
        "source_generated_utc": "2026-11-19T12:29:23.371326Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "SchedulingQaoaKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[Zero, One, One, Zero]",
            "count": 30
          },
          {
            "outcome": "[Zero, Zero, One, One]",
            "count": 27
          },
          {
            "outcome": "[Zero, One, Zero, One]",
            "count": 25
          },
          {
            "outcome": "[One, Zero, Zero, One]",
            "count": 20
          },
          {
            "outcome": "[One, Zero, One, One]",
            "count": 18
          },
          {
            "outcome": "[One, Zero, One, Zero]",
            "count": 16
          },
          {
            "outcome": "[One, One, Zero, Zero]",
            "count": 15
          },
          {
            "outcome": "[Zero, One, Zero, Zero]",
            "count": 15
          },
          {
            "outcome": "[Zero, Zero, One, Zero]",
            "count": 14
          },
          {
            "outcome": "[One, One, Zero, One]",
            "count": 9
          },
          {
            "outcome": "[One, One, One, Zero]",
            "count": 3
          },
          {
            "outcome": "[Zero, Zero, Zero, One]",
            "count": 3
          },
          {
            "outcome": "[One, Zero, Zero, Zero]",
            "count": 2
          },
          {
            "outcome": "[Zero, One, One, One]",
            "count": 2
          },
          {
            "outcome": "[One, One, One, One]",
            "count": 1
          }
        ]
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation.",
        "Archived problem; not an active quantum-advantage candidate."
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
            "0": 116,
            "1": 84
          },
          "p0": 0.58,
          "p1": 0.42,
          "z": 0.16,
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
            "0": 100,
            "1": 100
          },
          "p0": 0.5,
          "p1": 0.5,
          "z": 0.0,
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
            "0": 89,
            "1": 111
          },
          "p0": 0.445,
          "p1": 0.555,
          "z": -0.11,
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
            "0": 95,
            "1": 105
          },
          "p0": 0.475,
          "p1": 0.525,
          "z": -0.05,
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
        "sha256": "4d82a9744ec6cffe35d3881c5127385b660e5378a74932b2692db5ea407fa5c9"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "cddf7aee2b726d1acf5792a5c5253e563c15241defe829579ce20ec99572f53d"
        },
        "source_generated_utc": "2026-11-19T12:29:23.371326Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "ClimateHHLKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[One, Zero]",
            "count": 85
          },
          {
            "outcome": "[Zero, One]",
            "count": 49
          },
          {
            "outcome": "[Zero, Zero]",
            "count": 46
          },
          {
            "outcome": "[One, One]",
            "count": 20
          }
        ]
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation.",
        "Archived problem; not an active quantum-advantage candidate."
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
            "0": 95,
            "1": 105
          },
          "p0": 0.475,
          "p1": 0.525,
          "z": -0.05,
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
            "0": 131,
            "1": 69
          },
          "p0": 0.655,
          "p1": 0.345,
          "z": 0.31,
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
        "sha256": "4d82a9744ec6cffe35d3881c5127385b660e5378a74932b2692db5ea407fa5c9"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "cddf7aee2b726d1acf5792a5c5253e563c15241defe829579ce20ec99572f53d"
        },
        "source_generated_utc": "2026-11-19T12:29:23.371326Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "MaterialsQPEKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[One, Zero]",
            "count": 131
          },
          {
            "outcome": "[Zero, Zero]",
            "count": 35
          },
          {
            "outcome": "[One, One]",
            "count": 26
          },
          {
            "outcome": "[Zero, One]",
            "count": 8
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
            "0": 43,
            "1": 157
          },
          "p0": 0.215,
          "p1": 0.785,
          "z": -0.57,
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
            "0": 166,
            "1": 34
          },
          "p0": 0.83,
          "p1": 0.17,
          "z": 0.66,
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
        "sha256": "4d82a9744ec6cffe35d3881c5127385b660e5378a74932b2692db5ea407fa5c9"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "cddf7aee2b726d1acf5792a5c5253e563c15241defe829579ce20ec99572f53d"
        },
        "source_generated_utc": "2026-11-19T12:29:23.371326Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "GroverSearchKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[Zero, One, One, One]",
            "count": 197
          },
          {
            "outcome": "[One, One, One, One]",
            "count": 1
          },
          {
            "outcome": "[One, Zero, One, Zero]",
            "count": 1
          },
          {
            "outcome": "[Zero, Zero, Zero, Zero]",
            "count": 1
          }
        ]
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation.",
        "Archived problem; not an active quantum-advantage candidate."
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
            "0": 198,
            "1": 2
          },
          "p0": 0.99,
          "p1": 0.01,
          "z": 0.98,
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
            "0": 2,
            "1": 198
          },
          "p0": 0.01,
          "p1": 0.99,
          "z": -0.98,
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
            "0": 1,
            "1": 199
          },
          "p0": 0.005,
          "p1": 0.995,
          "z": -0.99,
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
            "0": 2,
            "1": 198
          },
          "p0": 0.01,
          "p1": 0.99,
          "z": -0.98,
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
        "sha256": "4d82a9744ec6cffe35d3881c5127385b660e5378a74932b2692db5ea407fa5c9"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "cddf7aee2b726d1acf5792a5c5253e563c15241defe829579ce20ec99572f53d"
        },
        "source_generated_utc": "2026-11-19T12:29:23.371326Z",
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
        "sha256": "4d82a9744ec6cffe35d3881c5127385b660e5378a74932b2692db5ea407fa5c9"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "cddf7aee2b726d1acf5792a5c5253e563c15241defe829579ce20ec99572f53d"
        },
        "source_generated_utc": "2026-11-19T12:29:23.371326Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "NuclearQPEKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[One, Zero]",
            "count": 124
          },
          {
            "outcome": "[Zero, Zero]",
            "count": 34
          },
          {
            "outcome": "[One, One]",
            "count": 30
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
            "0": 46,
            "1": 154
          },
          "p0": 0.23,
          "p1": 0.77,
          "z": -0.54,
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
            "0": 158,
            "1": 42
          },
          "p0": 0.79,
          "p1": 0.21,
          "z": 0.58,
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
        "sha256": "4d82a9744ec6cffe35d3881c5127385b660e5378a74932b2692db5ea407fa5c9"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "cddf7aee2b726d1acf5792a5c5253e563c15241defe829579ce20ec99572f53d"
        },
        "source_generated_utc": "2026-11-19T12:29:23.371326Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "QuantumWalkKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[One, Zero, Zero]",
            "count": 97
          },
          {
            "outcome": "[Zero, Zero, Zero]",
            "count": 42
          },
          {
            "outcome": "[Zero, One, Zero]",
            "count": 39
          },
          {
            "outcome": "[One, One, Zero]",
            "count": 22
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
            "0": 81,
            "1": 119
          },
          "p0": 0.405,
          "p1": 0.595,
          "z": -0.19,
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
            "0": 139,
            "1": 61
          },
          "p0": 0.695,
          "p1": 0.305,
          "z": 0.39,
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
        "sha256": "4d82a9744ec6cffe35d3881c5127385b660e5378a74932b2692db5ea407fa5c9"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "cddf7aee2b726d1acf5792a5c5253e563c15241defe829579ce20ec99572f53d"
        },
        "source_generated_utc": "2026-11-19T12:29:23.371326Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "LatticeGaugeKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[Zero, Zero, Zero, Zero]",
            "count": 94
          },
          {
            "outcome": "[Zero, Zero, Zero, One]",
            "count": 26
          },
          {
            "outcome": "[One, Zero, Zero, Zero]",
            "count": 19
          },
          {
            "outcome": "[One, Zero, Zero, One]",
            "count": 15
          },
          {
            "outcome": "[One, One, Zero, Zero]",
            "count": 12
          },
          {
            "outcome": "[Zero, Zero, One, One]",
            "count": 12
          },
          {
            "outcome": "[Zero, One, One, Zero]",
            "count": 6
          },
          {
            "outcome": "[One, One, One, One]",
            "count": 3
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
            "outcome": "[Zero, One, Zero, One]",
            "count": 2
          },
          {
            "outcome": "[Zero, One, Zero, Zero]",
            "count": 2
          },
          {
            "outcome": "[One, One, One, Zero]",
            "count": 1
          },
          {
            "outcome": "[One, One, Zero, One]",
            "count": 1
          },
          {
            "outcome": "[One, Zero, One, Zero]",
            "count": 1
          },
          {
            "outcome": "[Zero, One, One, One]",
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
            "0": 146,
            "1": 54
          },
          "p0": 0.73,
          "p1": 0.27,
          "z": 0.46,
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
            "0": 172,
            "1": 28
          },
          "p0": 0.86,
          "p1": 0.14,
          "z": 0.72,
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
            "0": 171,
            "1": 29
          },
          "p0": 0.855,
          "p1": 0.145,
          "z": 0.71,
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
            "0": 138,
            "1": 62
          },
          "p0": 0.69,
          "p1": 0.31,
          "z": 0.38,
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
        "sha256": "4d82a9744ec6cffe35d3881c5127385b660e5378a74932b2692db5ea407fa5c9"
      },
      "run": {
        "status": "available",
        "source": {
          "path": "website/data/simulatorMatrix.json",
          "sha256": "cddf7aee2b726d1acf5792a5c5253e563c15241defe829579ce20ec99572f53d"
        },
        "source_generated_utc": "2026-11-19T12:29:23.371326Z",
        "execution": "local-simulator",
        "target": "local-simulator",
        "entry_point": "MissionQaoaKernel",
        "shots": 200,
        "histogram": [
          {
            "outcome": "[Zero, One, One, Zero]",
            "count": 23
          },
          {
            "outcome": "[Zero, One, Zero, Zero]",
            "count": 20
          },
          {
            "outcome": "[One, Zero, Zero, Zero]",
            "count": 19
          },
          {
            "outcome": "[Zero, Zero, One, One]",
            "count": 19
          },
          {
            "outcome": "[One, One, Zero, Zero]",
            "count": 18
          },
          {
            "outcome": "[Zero, Zero, One, Zero]",
            "count": 18
          },
          {
            "outcome": "[One, Zero, One, Zero]",
            "count": 17
          },
          {
            "outcome": "[Zero, One, Zero, One]",
            "count": 13
          },
          {
            "outcome": "[Zero, Zero, Zero, One]",
            "count": 11
          },
          {
            "outcome": "[One, One, One, Zero]",
            "count": 9
          },
          {
            "outcome": "[One, Zero, Zero, One]",
            "count": 9
          },
          {
            "outcome": "[Zero, One, One, One]",
            "count": 9
          },
          {
            "outcome": "[One, One, Zero, One]",
            "count": 6
          },
          {
            "outcome": "[One, One, One, One]",
            "count": 4
          },
          {
            "outcome": "[One, Zero, One, One]",
            "count": 3
          },
          {
            "outcome": "[Zero, Zero, Zero, Zero]",
            "count": 2
          }
        ]
      },
      "warnings": [
        "Resource estimates and sampled kernel outcomes describe different programs. Neither demonstrates quantum advantage; this is not a quantum-state animation.",
        "Archived problem; not an active quantum-advantage candidate."
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
            "0": 115,
            "1": 85
          },
          "p0": 0.575,
          "p1": 0.425,
          "z": 0.15,
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
            "0": 98,
            "1": 102
          },
          "p0": 0.49,
          "p1": 0.51,
          "z": -0.02,
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
            "0": 98,
            "1": 102
          },
          "p0": 0.49,
          "p1": 0.51,
          "z": -0.02,
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
            "0": 126,
            "1": 74
          },
          "p0": 0.63,
          "p1": 0.37,
          "z": 0.26,
          "x": null,
          "y": null,
          "representation": "measurement-derived diagonal-state representation"
        }
      ]
    }
  ]
};
