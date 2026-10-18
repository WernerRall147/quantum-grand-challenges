/-- Majority of three bits. -/
def majority3 (a b c : Bool) : Bool := (a && b) || (a && c) || (b && c)

/-- Sending 0 through a distance-3 repetition code, majority decoding fails exactly when at
least two of the three bits flip. Checked over all eight flip patterns. -/
theorem rep3_fails_iff (a b c : Bool) :
    majority3 a b c = true ↔ 2 ≤ a.toNat + b.toNat + c.toNat := by
  cases a <;> cases b <;> cases c <;> decide
