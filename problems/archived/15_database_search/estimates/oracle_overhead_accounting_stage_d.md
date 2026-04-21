# Oracle And Transpilation Overhead Accounting - Stage D

This report models how per-round oracle/transpilation overhead changes practical speedup interpretation.

## Instance: large

| Oracle/Transpile Cost Factor | Effective Quantum Query-Equivalent | Effective Speedup |
|---:|---:|---:|
| 1 | 145583.00 | 1086888.19x |
| 10 | 1455830.00 | 108688.82x |
| 100 | 14558300.00 | 10868.88x |
| 1000 | 145583000.00 | 1086.89x |

## Instance: medium

| Oracle/Transpile Cost Factor | Effective Quantum Query-Equivalent | Effective Speedup |
|---:|---:|---:|
| 1 | 24.00 | 127.76x |
| 10 | 240.00 | 12.78x |
| 100 | 2400.00 | 1.28x |
| 1000 | 24000.00 | 0.13x |

## Instance: small

| Oracle/Transpile Cost Factor | Effective Quantum Query-Equivalent | Effective Speedup |
|---:|---:|---:|
| 1 | 4.00 | 23.59x |
| 10 | 40.00 | 2.36x |
| 100 | 400.00 | 0.24x |
| 1000 | 4000.00 | 0.02x |

