namespace QuantumGrandChallenges.LinearSolvers {
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Math;

    function Determinant2x2(matrix : Double[][]) : Double {
        let a = matrix[0][0];
        let b = matrix[0][1];
        let c = matrix[1][0];
        let d = matrix[1][1];
        return a * d - b * c;
    }

    function SolveSymmetric2x2(matrix : Double[][], rhs : Double[]) : Double[] {
        let det = Determinant2x2(matrix);
    if AbsD(det) < 1e-9 {
            fail "Matrix is singular; cannot compute analytical baseline.";
        }

        let a = matrix[0][0];
        let b = matrix[0][1];
        let d = matrix[1][1];
        let f0 = rhs[0];
        let f1 = rhs[1];

        let x0 = (d * f0 - b * f1) / det;
        let x1 = (-b * f0 + a * f1) / det;

        return [x0, x1];
    }

    function ConditionNumberSymmetric2x2(matrix : Double[][]) : Double {
        let a = matrix[0][0];
        let b = matrix[0][1];
        let d = matrix[1][1];
        let trace = a + d;
        let delta = Sqrt((a - d) * (a - d) + 4.0 * b * b);
        let lambdaMax = 0.5 * (trace + delta);
        let lambdaMin = 0.5 * (trace - delta);
    if AbsD(lambdaMin) < 1e-12 {
            fail "Condition number undefined because the minimum eigenvalue is zero.";
        }
        return lambdaMax / lambdaMin;
    }

    function ResidualNorm(matrix : Double[][], solution : Double[], rhs : Double[]) : Double {
        let a00 = matrix[0][0];
        let a01 = matrix[0][1];
        let a10 = matrix[1][0];
        let a11 = matrix[1][1];
        let r0 = a00 * solution[0] + a01 * solution[1] - rhs[0];
        let r1 = a10 * solution[0] + a11 * solution[1] - rhs[1];
        return Sqrt(r0 * r0 + r1 * r1);
    }

    @EntryPoint()
    operation RunLinearSolverBaseline() : Unit {
        Message("Analytical baseline for the 2x2 Poisson-style system");
        Message("--------------------------------------------------");

        let matrix = [[4.0, -1.0], [-1.0, 3.0]];
        let rhs = [15.0, 10.0];

        let solution = SolveSymmetric2x2(matrix, rhs);
        let conditionNumber = ConditionNumberSymmetric2x2(matrix);
        let residual = ResidualNorm(matrix, solution, rhs);

        Message($"Matrix: {matrix}");
        Message($"RHS: {rhs}");
        Message($"Solution vector: {solution}");
        Message($"Condition number (2-norm): {conditionNumber}");
        Message($"Residual norm: {residual}");
        Message("Next step: replace analytical solve with block-encoding and phase estimation for arbitrary instances.");
    }
}
