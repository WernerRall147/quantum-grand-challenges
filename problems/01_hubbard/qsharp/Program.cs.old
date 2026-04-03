using System;
using System.Globalization;
using System.Threading.Tasks;
using Microsoft.Quantum.Simulation.Simulators;

namespace QuantumGrandChallenges.Hubbard
{
    internal static class Program
    {
        private static readonly CultureInfo Culture = CultureInfo.InvariantCulture;

        private static async Task<int> RunAnalysisAsync()
        {
            using var simulator = new QuantumSimulator();
            await RunTwoSiteHubbardAnalysis.Run(simulator);
            return 0;
        }

        private static async Task<int> RunEnergyEstimateAsync(string[] args)
        {
            if (args.Length < 6)
            {
                Console.Error.WriteLine("Usage: dotnet run --project problems/01_hubbard/qsharp/Hubbard.csproj -- energy t u theta0 theta1 theta2 shots");
                return 1;
            }

            double t = double.Parse(args[0], Culture);
            double u = double.Parse(args[1], Culture);
            double theta0 = double.Parse(args[2], Culture);
            double theta1 = double.Parse(args[3], Culture);
            double theta2 = double.Parse(args[4], Culture);
            int shots = int.Parse(args[5], Culture);

            using var simulator = new QuantumSimulator();
            double energy = await EstimateHubbardEnergy.Run(simulator, t, u, theta0, theta1, theta2, shots);
            Console.WriteLine(energy.ToString("G17", Culture));
            return 0;
        }

        public static int Main(string[] args)
        {
            if (args.Length == 0 || string.Equals(args[0], "analysis", StringComparison.OrdinalIgnoreCase))
            {
                return RunAnalysisAsync().GetAwaiter().GetResult();
            }

            if (string.Equals(args[0], "energy", StringComparison.OrdinalIgnoreCase))
            {
                return RunEnergyEstimateAsync(args[1..]).GetAwaiter().GetResult();
            }

            Console.Error.WriteLine("Unknown mode. Use 'analysis' or 'energy'.");
            return 1;
        }
    }
}
