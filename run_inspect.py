import json
d = json.load(open('website/data/multiModelEstimates.json'))
print(f"Total: {d['total_estimates']} estimates, {d['total_failures']} failures, {d['elapsed_seconds']}s")
print(f"Problems: {len(d['problems'])}")
for p in sorted(d['problems']):
    models = d['problems'][p]['models']
    print(f"  {p}: {len(models)} configs")
    qubits = [v['physicalQubits'] for v in models.values() if v.get('physicalQubits')]
    if qubits:
        print(f"    Physical qubits range: {min(qubits):,} - {max(qubits):,} ({max(qubits)/min(qubits):.1f}x)")
