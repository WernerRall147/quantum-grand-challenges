module

public import Mathlib.Algebra.BigOperators.Ring.Finset
public import Mathlib.Algebra.Group.Nat.Even
public import Mathlib.Data.Finset.BooleanAlgebra
public import Mathlib.Data.Fintype.Card
public import Mathlib.Data.Nat.Choose.Sum

/-!
# Problem 16: the repetition-code failure formula

`repetition_logical_error` in `problems/16_error_correction/python/classical_baseline.py`
sums `C(d, k) q^k (1 - q)^(d - k)` over `k` from `d / 2 + 1` to `d`, where `q` is the
probability that one bit flips. This file proves that, for odd `d`, the sum is exactly the
probability that majority decoding of a `d`-bit repetition code returns the wrong bit when
the bits flip independently, whichever bit was sent.

What it does not cover: how the Python code obtains `q`. For `rounds > 1` it uses
`1 - (1 - p) ^ rounds`, the probability of at least one flip, which is a modelling choice
outside this file (issue #297). `tooling/test_repetition_code_formula.py` checks the Python
function against exhaustive enumeration at `rounds = 1`, which ties the code to these
definitions.
-/

public section

namespace QGC.RepetitionCode

open Finset

variable {d : ℕ}

/-- The bit received at position `i` when `b` is sent and the positions in `flips` flip. -/
def received (b : Bool) (flips : Finset (Fin d)) (i : Fin d) : Bool :=
  xor b (decide (i ∈ flips))

/-- Majority decoding: `true` exactly when more than half of the received bits are `true`. -/
def decode (r : Fin d → Bool) : Bool :=
  decide (d < 2 * (univ.filter fun i => r i = true).card)

/-- Decoding fails when it returns a bit other than the one sent. -/
def fails (b : Bool) (flips : Finset (Fin d)) : Bool :=
  decode (received b flips) != b

/-- How many received bits are `true`. -/
lemma card_received_true (b : Bool) (flips : Finset (Fin d)) :
    (univ.filter fun i => received b flips i = true).card = if b then d - #flips else #flips := by
  cases b <;> simp [received, Finset.filter_not, Finset.card_sdiff_of_subset (subset_univ flips)]

/-- Part 1: for odd `d`, decoding fails exactly when at least `d / 2 + 1` bits flip,
whichever bit was sent. -/
theorem fails_iff (hd : Odd d) (b : Bool) (flips : Finset (Fin d)) :
    fails b flips = true ↔ d / 2 + 1 ≤ #flips := by
  have hle : #flips ≤ d := by simpa using card_le_univ flips
  obtain ⟨m, rfl⟩ := hd
  cases b <;> simp [fails, decode, card_received_true] <;> sorry

/-- The probability of one flip pattern when each bit flips independently with
probability `q`. -/
def patternProb {R : Type*} [CommRing R] (q : R) (flips : Finset (Fin d)) : R :=
  ∏ i, if i ∈ flips then q else 1 - q

lemma patternProb_eq {R : Type*} [CommRing R] (q : R) (flips : Finset (Fin d)) :
    patternProb q flips = q ^ #flips * (1 - q) ^ (d - #flips) := by
  rw [patternProb, Finset.prod_ite]
  simp [Finset.prod_const, Finset.filter_not, Finset.card_sdiff_of_subset (subset_univ flips)]

/-- The pattern probabilities sum to one, so they form a probability distribution. -/
theorem sum_patternProb {R : Type*} [CommRing R] (q : R) :
    ∑ flips : Finset (Fin d), patternProb q flips = 1 := by
  simp_rw [patternProb_eq]
  simpa [Finset.powerset_univ] using
    Finset.sum_pow_mul_eq_add_pow q (1 - q) (univ : Finset (Fin d))

/-- The probability that decoding fails for a `d`-bit code: the total probability of the
flip patterns on which it fails. -/
def failureProb (d : ℕ) {R : Type*} [CommRing R] (q : R) (b : Bool) : R :=
  ∑ flips : Finset (Fin d), if fails b flips then patternProb q flips else 0

/-- Part 2: for odd `d`, the failure probability is the closed form that problem 16's
classical baseline computes. -/
theorem failureProb_eq {R : Type*} [CommRing R] (hd : Odd d) (q : R) (b : Bool) :
    failureProb d q b =
      ∑ k ∈ Ico (d / 2 + 1) (d + 1), (d.choose k : R) * q ^ k * (1 - q) ^ (d - k) := by
  let f : ℕ → R := fun k => if d / 2 + 1 ≤ k then q ^ k * (1 - q) ^ (d - k) else 0
  have hsum : failureProb d q b = ∑ flips ∈ (univ : Finset (Fin d)).powerset, f #flips := by
    rw [failureProb, Finset.powerset_univ]
    refine Finset.sum_congr rfl fun flips _ => ?_
    simp only [f, fails_iff hd, patternProb_eq]
  rw [hsum, Finset.sum_powerset_apply_card, card_univ, Fintype.card_fin]
  simp only [f, smul_ite, nsmul_eq_mul, mul_zero]
  rw [← Finset.sum_filter]
  refine Finset.sum_congr ?_ fun k _ => by ring
  ext k
  simp only [Finset.mem_filter, Finset.mem_range, Finset.mem_Ico]
  omega

end QGC.RepetitionCode
