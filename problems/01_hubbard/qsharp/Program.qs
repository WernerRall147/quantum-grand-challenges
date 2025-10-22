namespace QuantumGrandChallenges.Hubbard {
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;

    function SingletEigenvalue(t : Double, u : Double) : Double {
        let discriminant = Sqrt(u * u + 16.0 * t * t);
        // Negative branch gives the singlet (ground) energy for half filling
        return 0.5 * (u - discriminant);
    }

    function UpperSingletEigenvalue(t : Double, u : Double) : Double {
        let discriminant = Sqrt(u * u + 16.0 * t * t);
        return 0.5 * (u + discriminant);
    }

    function TripletEigenvalue(u : Double) : Double {
        // Two-site Hubbard triplet state has no double occupation penalty
        return 0.0;
    }

    @EntryPoint()
    operation RunTwoSiteHubbardAnalysis() : Unit {
        use marker = Qubit();
        Reset(marker);

        let hoppingStrengths = [0.5, 1.0];
        let interactionStrengths = [0.0, 2.0, 4.0, 8.0];

        Message("Two-site Hubbard model at half filling (one electron per site)");
        Message("-----------------------------------------------------------");

        for t in hoppingStrengths {
            for u in interactionStrengths {
                let gs = SingletEigenvalue(t, u);
                let excited = UpperSingletEigenvalue(t, u);
                let triplet = TripletEigenvalue(u);
                let chargeGap = excited - gs;
                let spinGap = triplet - gs;

                Message($"t = {t}, U = {u}");
                Message($"  Ground state energy (singlet) : {gs}");
                Message($"  Upper singlet energy         : {excited}");
                Message($"  Triplet energy               : {triplet}");
                Message($"  Charge gap Δc                : {chargeGap}");
                Message($"  Spin gap Δs                  : {spinGap}");
            }
        }

        Message("\nNext step: replace analytical energies with variational or phase-estimation-based routines.");
    }
}
