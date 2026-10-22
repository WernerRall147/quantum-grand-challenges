module

public import QGC.RepetitionCode

/-!
# Axiom audit

Every theorem that backs a claim in this repository may rest only on Lean's three standard
axioms. Anything that skips the kernel's check adds another axiom (`sorryAx` or
`Lean.ofReduceBool`), changes the output below, and fails the build.
-/

/--
info: 'QGC.RepetitionCode.fails_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms QGC.RepetitionCode.fails_iff

/--
info: 'QGC.RepetitionCode.sum_patternProb' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms QGC.RepetitionCode.sum_patternProb

/--
info: 'QGC.RepetitionCode.failureProb_eq' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms QGC.RepetitionCode.failureProb_eq
