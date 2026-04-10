namespace QuantumGrandChallenges.ErrorCorrection {
    open Microsoft.Quantum.Arrays;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Diagnostics;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;

    /// Encode a single logical qubit into 3 physical qubits (bit-flip code).
    /// |0⟩_L = |000⟩, |1⟩_L = |111⟩
    operation Encode3BitRepetition(data : Qubit, ancilla1 : Qubit, ancilla2 : Qubit) : Unit is Adj + Ctl {
        CNOT(data, ancilla1);
        CNOT(data, ancilla2);
    }

    /// Extract syndrome bits via parity checks.
    /// syndrome[0] = data ⊕ ancilla1, syndrome[1] = ancilla1 ⊕ ancilla2
    operation ExtractSyndrome(code : Qubit[], syndromes : Qubit[]) : Unit {
        // Parity check: qubit 0 vs qubit 1
        CNOT(code[0], syndromes[0]);
        CNOT(code[1], syndromes[0]);
        // Parity check: qubit 1 vs qubit 2
        CNOT(code[1], syndromes[1]);
        CNOT(code[2], syndromes[1]);
    }

    /// Apply correction based on syndrome measurement.
    /// Syndrome 00 = no error, 10 = qubit 0, 11 = qubit 1, 01 = qubit 2
    operation ApplyCorrection(code : Qubit[], s0 : Result, s1 : Result) : Unit {
        if (s0 == One and s1 == Zero) {
            X(code[0]);
        } elif (s0 == One and s1 == One) {
            X(code[1]);
        } elif (s0 == Zero and s1 == One) {
            X(code[2]);
        }
        // s0==Zero, s1==Zero => no error
    }

    /// Simulate a bit-flip error on qubit at index errorIdx (-1 = no error).
    operation InjectBitFlipError(code : Qubit[], errorIdx : Int) : Unit {
        if (errorIdx >= 0 and errorIdx < Length(code)) {
            X(code[errorIdx]);
        }
    }

    /// Full encode-error-correct-decode cycle. Returns (corrected, original_matched).
    operation RunRepetitionCodeCycle(prepareOne : Bool, errorIdx : Int) : (Result, Bool) {
        use code = Qubit[3];
        use syndromes = Qubit[2];

        // Prepare logical state
        if (prepareOne) {
            X(code[0]);
        }

        // Encode
        Encode3BitRepetition(code[0], code[1], code[2]);

        // Inject error
        InjectBitFlipError(code, errorIdx);

        // Syndrome extraction
        ExtractSyndrome(code, syndromes);
        let s0 = M(syndromes[0]);
        let s1 = M(syndromes[1]);

        // Correction
        ApplyCorrection(code, s0, s1);

        // Decode (reverse encoding)
        CNOT(code[0], code[2]);
        CNOT(code[0], code[1]);

        // Measure logical qubit
        let result = M(code[0]);

        mutable matched = false;
        if (prepareOne) {
            set matched = result == One;
        } else {
            set matched = result == Zero;
        }

        ResetAll(code);
        ResetAll(syndromes);

        return (result, matched);
    }

    /// Run statistical trials of the repetition code.
    operation RunTrials(prepareOne : Bool, errorIdx : Int, shots : Int) : (Int, Int) {
        mutable correctedCount = 0;
        for _ in 1 .. shots {
            let (_, matched) = RunRepetitionCodeCycle(prepareOne, errorIdx);
            if (matched) {
                set correctedCount += 1;
            }
        }
        return (correctedCount, shots);
    }

    @EntryPoint()
    operation RunQECDemonstration() : Unit {
        Message("=== Quantum Error Correction: 3-Qubit Bit-Flip Repetition Code ===");
        Message("");
        Message("Code: |0⟩_L = |000⟩, |1⟩_L = |111⟩");
        Message("Corrects any single bit-flip (X) error on one of 3 qubits.");
        Message("");

        let shots = 64;

        // Test all error scenarios
        let scenarios = [
            (false, -1, "No error, |0⟩_L"),
            (false, 0,  "Error on qubit 0, |0⟩_L"),
            (false, 1,  "Error on qubit 1, |0⟩_L"),
            (false, 2,  "Error on qubit 2, |0⟩_L"),
            (true,  -1, "No error, |1⟩_L"),
            (true,  0,  "Error on qubit 0, |1⟩_L"),
            (true,  1,  "Error on qubit 1, |1⟩_L"),
            (true,  2,  "Error on qubit 2, |1⟩_L")
        ];

        mutable totalCorrect = 0;
        mutable totalTrials = 0;

        for (prepOne, errIdx, label) in scenarios {
            let (correct, total) = RunTrials(prepOne, errIdx, shots);
            let rate = IntAsDouble(correct) / IntAsDouble(total) * 100.0;
            Message($"  {label}: {correct}/{total} correct ({rate}%)");
            set totalCorrect += correct;
            set totalTrials += total;
        }

        Message("");
        let overallRate = IntAsDouble(totalCorrect) / IntAsDouble(totalTrials) * 100.0;
        Message($"Overall correction rate: {totalCorrect}/{totalTrials} ({overallRate}%)");
        Message("");
        Message("=== Error Correction Theory ===");
        Message("Without QEC: single bit-flip destroys the state (0% recovery).");
        Message("With 3-qubit code: any single-qubit X error is correctable (100% recovery).");
        Message("Threshold theorem: if physical error rate p < threshold,");
        Message("logical error rate decreases exponentially with code distance.");
    }
}
