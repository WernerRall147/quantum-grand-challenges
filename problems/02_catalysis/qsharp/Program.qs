namespace QuantumGrandChallenges.Catalysis {
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math as Math;

    function ArrheniusRate(preExponential : Double, activationEnergy : Double, temperature : Double) : Double {
        let gasConstant = 8.314; // J · mol⁻¹ · K⁻¹
        let exponent = -activationEnergy / (gasConstant * temperature);
        return preExponential * Math.ExpD(exponent);
    }

    @EntryPoint()
    operation RunAnalyticalCatalysisBaseline() : Unit {
        use marker = Qubit();
        Reset(marker);

        let instances = [
            ("small", "H2 + O2 -> H2O", 300.0, 1.0, "Pt", 2, 1.0e13, 75000.0),
            ("medium", "N2 + 3H2 -> 2NH3", 500.0, 10.0, "Fe", 4, 5.0e12, 95000.0),
            ("large", "CO2 + 2H2 -> CO + H2O", 700.0, 20.0, "Cu", 8, 2.0e13, 105000.0)
        ];

        Message("Analytical Arrhenius rates for catalysis instances:");
        Message("---------------------------------------------------");

        for (instanceId, reaction, temperature, pressure, catalyst, activeSites, preExponential, activationEnergy) in instances {
            let rate = ArrheniusRate(preExponential, activationEnergy, temperature);
            Message($"Instance: {instanceId}");
            Message($"  Reaction: {reaction}");
            Message($"  Catalyst: {catalyst} ({activeSites} active sites)");
            Message($"  Temperature: {temperature} K, Pressure: {pressure} atm");
            Message($"  Reaction rate: {rate} s^-1");
        }

        Message("\nNext step: integrate VQE/PEA chemistry routines for realistic energy surfaces.");
    }
}
