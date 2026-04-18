import subprocess, sys, os, time

os.environ['PYTHONUTF8'] = '1'
os.environ['MPLBACKEND'] = 'Agg'
os.chdir(r'C:\Users\weral\Git\quantum-grand-challenges')

problems = [
    "01_hubbard","02_catalysis","03_qae_risk","04_linear_solvers","05_qaoa_maxcut",
    "06_high_frequency_trading","07_drug_discovery","08_protein_folding","09_factorization",
    "10_post_quantum_cryptography","11_quantum_machine_learning","12_quantum_optimization",
    "13_climate_modeling","14_materials_discovery","15_database_search","16_error_correction",
    "17_nuclear_physics","18_photovoltaics","19_quantum_chromodynamics","20_space_mission_planning"
]

results = []
for p in problems:
    script = f"problems/{p}/python/classical_baseline.py"
    if not os.path.exists(script):
        results.append((p, "SKIPPED"))
        print(f"{p:40s} SKIPPED", flush=True)
        continue
    try:
        env = os.environ.copy()
        env['MPLBACKEND'] = 'Agg'
        t0 = time.time()
        r = subprocess.run(
            [sys.executable, script],
            capture_output=True, text=True, timeout=30,
            cwd=os.getcwd(), env=env
        )
        elapsed = time.time() - t0
        if r.returncode == 0:
            results.append((p, "SUCCESS"))
            print(f"{p:40s} SUCCESS ({elapsed:.1f}s)", flush=True)
        else:
            err_last = r.stderr.strip().split('\n')[-1] if r.stderr.strip() else ""
            results.append((p, f"FAILED (exit {r.returncode})"))
            print(f"{p:40s} FAILED (exit {r.returncode}, {elapsed:.1f}s) {err_last[:120]}", flush=True)
    except subprocess.TimeoutExpired:
        results.append((p, "FAILED (timeout)"))
        print(f"{p:40s} FAILED (timeout)", flush=True)
    except Exception as e:
        results.append((p, f"ERROR: {e}"))
        print(f"{p:40s} ERROR: {e}", flush=True)

print("\n===== SUMMARY =====", flush=True)
print(f"{'Problem':<40s} {'Status'}", flush=True)
print("-"*70, flush=True)
for p, s in results:
    print(f"{p:<40s} {s}", flush=True)
suc = sum(1 for _,s in results if s=="SUCCESS")
fail = sum(1 for _,s in results if s.startswith("FAILED"))
skip = sum(1 for _,s in results if s=="SKIPPED")
print(f"\nTotal: {len(results)} | Success: {suc} | Failed: {fail} | Skipped: {skip}", flush=True)
