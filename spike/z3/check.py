"""ADR 0002 spike: the three-bit repetition-code statement, checked by Z3."""

from z3 import And, Bools, If, Not, Or, Solver, unsat

a, b, c = Bools("a b c")
majority = Or(And(a, b), And(a, c), And(b, c))
flips = If(a, 1, 0) + If(b, 1, 0) + If(c, 1, 0)

solver = Solver()
solver.add(Not(majority == (flips >= 2)))
result = solver.check()
print(f"z3 result: {result} (unsat means the statement holds for every pattern)")
if result != unsat:
    raise SystemExit(f"counterexample: {solver.model()}")
