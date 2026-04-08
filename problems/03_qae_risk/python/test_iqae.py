"""Quick validation of IQAE round measurements."""
import math, qsharp

qsharp.init(project_root="problems/03_qae_risk/qsharp")

tail = qsharp.eval("Main.TailProbability(Main.LogNormalProbabilities(4, 0.0, 1.0), 2.5, 4)")
print(f"Theoretical tail prob: {tail:.6f}")

theta = math.asin(math.sqrt(tail))
print(f"theta = {theta:.6f}")

for k in [0, 1, 2, 4]:
    expr = f"Main.IQAERound(Main.LogNormalProbabilities(4, 0.0, 1.0), 2.5, 4, {k})"
    results = qsharp.run(expr, 500)
    ones = sum(1 for r in results if str(r) == "One")
    measured = ones / 500
    expected = math.sin((2 * k + 1) * theta) ** 2
    print(f"  k={k}: {ones}/500 = {measured:.4f}  expected sin^2({2*k+1}*theta) = {expected:.4f}")
