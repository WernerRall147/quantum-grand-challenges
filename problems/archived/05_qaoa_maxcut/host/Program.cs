using System.Globalization;
using System.Text.Json;
using Microsoft.Quantum.Simulation.Core;
using Microsoft.Quantum.Simulation.Simulators;
using QuantumGrandChallenges.QaoaMaxCut;

namespace QuantumGrandChallenges.QaoaMaxCut.Driver;

internal sealed class GraphInstance
{
    public GraphInstance(string id)
    {
        Id = id;
    }

    public string Id { get; }
    public string Description { get; set; } = string.Empty;
    public List<string> Nodes { get; } = new();
    public List<(string U, string V, double Weight)> Edges { get; } = new();
    public double TargetPrecision { get; set; } = 0.02;
}

internal static class GraphLoader
{
    public static GraphInstance Load(string instancesDirectory, string instanceId)
    {
        var path = Path.Combine(instancesDirectory, instanceId + ".yaml");
        if (!File.Exists(path))
        {
            throw new FileNotFoundException($"Instance '{instanceId}' not found at {path}");
        }

        var instance = new GraphInstance(instanceId);
        foreach (var rawLine in File.ReadLines(path))
        {
            var line = rawLine.Trim();
            if (string.IsNullOrWhiteSpace(line) || line.StartsWith("#", StringComparison.Ordinal))
            {
                continue;
            }

            if (line.StartsWith("description:", StringComparison.Ordinal))
            {
                instance.Description = ExtractValue(line);
            }
            else if (line.StartsWith("nodes:", StringComparison.Ordinal))
            {
                foreach (var node in ExtractList(line))
                {
                    instance.Nodes.Add(node);
                }
            }
            else if (line.StartsWith("target_precision:", StringComparison.Ordinal))
            {
                instance.TargetPrecision = double.Parse(ExtractValue(line), CultureInfo.InvariantCulture);
            }
            else if (line.StartsWith("- [", StringComparison.Ordinal))
            {
                var parts = ExtractList(line).ToArray();
                if (parts.Length != 3)
                {
                    throw new InvalidDataException($"Edge entry '{line}' in {path} must contain three elements.");
                }

                instance.Edges.Add((parts[0], parts[1], double.Parse(parts[2], CultureInfo.InvariantCulture)));
            }
        }

        if (instance.Nodes.Count == 0)
        {
            throw new InvalidDataException($"Instance '{instanceId}' defines no nodes.");
        }

        return instance;
    }

    private static string ExtractValue(string line)
    {
        var colonIndex = line.IndexOf(':');
        var value = line[(colonIndex + 1)..].Trim();
        return value.Trim('"');
    }

    private static IEnumerable<string> ExtractList(string line)
    {
        var start = line.IndexOf('[');
        var end = line.LastIndexOf(']');
        if (start < 0 || end < 0 || end <= start)
        {
            yield break;
        }

        var inner = line.Substring(start + 1, end - start - 1);
        foreach (var item in inner.Split(',', StringSplitOptions.RemoveEmptyEntries))
        {
            yield return item.Trim().Trim('"');
        }
    }
}

internal static class WeightMatrixBuilder
{
    public static double[][] Build(GraphInstance instance)
    {
        var nodeIndex = instance.Nodes
            .Select((node, index) => (node, index))
            .ToDictionary(pair => pair.node, pair => pair.index, StringComparer.Ordinal);

        var n = instance.Nodes.Count;
        var matrix = new double[n][];
        for (var i = 0; i < n; i++)
        {
            matrix[i] = new double[n];
        }

        foreach (var (u, v, weight) in instance.Edges)
        {
            if (!nodeIndex.TryGetValue(u, out var i) || !nodeIndex.TryGetValue(v, out var j))
            {
                throw new InvalidDataException($"Edge references unknown nodes '{u}' or '{v}'.");
            }

            matrix[i][j] = weight;
            matrix[j][i] = weight;
        }

        return matrix;
    }
}

internal readonly record struct Parameters(
    string InstanceId,
    int Depth,
    int CoarseShots,
    int RefinedShots,
    int Trials,
    string? OutFile
);

internal readonly record struct TrialMetrics(
    int Trial,
    double[] BestBetas,
    double[] BestGammas,
    double BestBeta,
    double BestGamma,
    double CoarseExpectation,
    double RefinedExpectation,
    double RefinedBestSample,
    long[] RefinedAssignment
);

internal static class Program
{
    public static int Main(string[] args)
    {
        try
        {
            var parameters = ParseParameters(args);
            var baseDir = AppContext.BaseDirectory;
            var projectDir = Path.GetFullPath(Path.Combine(baseDir, "..", "..", ".."));
            var problemDir = Path.GetFullPath(Path.Combine(projectDir, ".."));
            var instancesDir = Path.Combine(problemDir, "instances");

            var instance = GraphLoader.Load(instancesDir, parameters.InstanceId);
            var weights = WeightMatrixBuilder.Build(instance);

            Console.WriteLine($"Instance    : {parameters.InstanceId} ({instance.Description})");
            Console.WriteLine($"Nodes       : {instance.Nodes.Count}");
            Console.WriteLine($"Edges       : {instance.Edges.Count}");
            Console.WriteLine($"Target ε    : {instance.TargetPrecision}");
            Console.WriteLine($"Depth       : {parameters.Depth}");
            Console.WriteLine($"Shots (coarse/refined): {parameters.CoarseShots}/{parameters.RefinedShots}");
            Console.WriteLine($"Trials      : {parameters.Trials}\n");

            var weightArray = ToQuantumArray(weights);
            var trials = new List<TrialMetrics>(capacity: parameters.Trials);
            double optimalValue = 0.0;
            long[] optimalAssignment = Array.Empty<long>();

            for (var trial = 1; trial <= parameters.Trials; trial++)
            {
                using var simulator = new QuantumSimulator(randomNumberGeneratorSeed: (uint)(1337 + trial));
                var result = RunQaoaAnalysis.Run(
                    simulator,
                    weightArray,
                    parameters.Depth,
                    parameters.CoarseShots,
                    parameters.RefinedShots
                ).Result;

                if (trial == 1)
                {
                    optimalValue = result.Item1;
                    optimalAssignment = result.Item2.ToArray();
                }

                var bestBetas = result.Item3.ToArray();
                var bestGammas = result.Item4.ToArray();
                var primaryBeta = bestBetas.Length > 0 ? bestBetas[0] : 0.0;
                var primaryGamma = bestGammas.Length > 0 ? bestGammas[0] : 0.0;

                trials.Add(new TrialMetrics(
                    Trial: trial,
                    BestBetas: bestBetas,
                    BestGammas: bestGammas,
                    BestBeta: primaryBeta,
                    BestGamma: primaryGamma,
                    CoarseExpectation: result.Item5,
                    RefinedExpectation: result.Item8,
                    RefinedBestSample: result.Item9,
                    RefinedAssignment: result.Item10.ToArray()
                ));
            }

            var coarseExpectations = trials.Select(t => t.CoarseExpectation).ToArray();
            var refinedExpectations = trials.Select(t => t.RefinedExpectation).ToArray();
            var refinedBestSamples = trials.Select(t => t.RefinedBestSample).ToArray();

            var (coarseMean, coarseStd, coarseCi95) = ComputeStats(coarseExpectations);
            var (refinedMean, refinedStd, refinedCi95) = ComputeStats(refinedExpectations);
            var (bestSampleMean, bestSampleStd, bestSampleCi95) = ComputeStats(refinedBestSamples);

            var bestTrial = trials.OrderByDescending(t => t.RefinedExpectation).First();

            Console.WriteLine($"Classical optimum value : {optimalValue}");
            Console.WriteLine($"Classical assignment    : {FormatAssignment(optimalAssignment)}\n");

            Console.WriteLine("QAOA coarse expectation across trials:");
            Console.WriteLine($"  Mean ± std : {coarseMean:F4} ± {coarseStd:F4}");
            Console.WriteLine($"  95% CI     : ±{coarseCi95:F4}\n");

            Console.WriteLine("QAOA refined expectation across trials:");
            Console.WriteLine($"  Mean ± std : {refinedMean:F4} ± {refinedStd:F4}");
            Console.WriteLine($"  95% CI     : ±{refinedCi95:F4}");
            Console.WriteLine($"  Gap to optimum (mean): {Math.Max(0.0, optimalValue - refinedMean):F4}\n");

            Console.WriteLine("Refined best-sample value across trials:");
            Console.WriteLine($"  Mean ± std : {bestSampleMean:F4} ± {bestSampleStd:F4}");
            Console.WriteLine($"  95% CI     : ±{bestSampleCi95:F4}\n");

            Console.WriteLine("Best trial parameters:");
            Console.WriteLine($"  Trial      : {bestTrial.Trial}");
            Console.WriteLine($"  Betas      : {FormatDoubleArray(bestTrial.BestBetas)}");
            Console.WriteLine($"  Gammas     : {FormatDoubleArray(bestTrial.BestGammas)}");
            Console.WriteLine($"  Primary β/γ: {bestTrial.BestBeta:F4} / {bestTrial.BestGamma:F4}");
            Console.WriteLine($"  Expectation: {bestTrial.RefinedExpectation:F4}");
            Console.WriteLine($"  Assignment : {FormatAssignment(bestTrial.RefinedAssignment)}");

            var outPath = ResolveOutputPath(parameters, problemDir);
            var report = new
            {
                problem_id = "05_qaoa_maxcut",
                instance_id = parameters.InstanceId,
                depth = parameters.Depth,
                coarse_shots = parameters.CoarseShots,
                refined_shots = parameters.RefinedShots,
                trials = parameters.Trials,
                classical_optimum = new
                {
                    value = optimalValue,
                    assignment = optimalAssignment,
                },
                aggregate = new
                {
                    coarse_expectation = new { mean = coarseMean, std = coarseStd, ci95 = coarseCi95 },
                    refined_expectation = new { mean = refinedMean, std = refinedStd, ci95 = refinedCi95 },
                    refined_best_sample = new { mean = bestSampleMean, std = bestSampleStd, ci95 = bestSampleCi95 },
                    mean_optimality_gap = Math.Max(0.0, optimalValue - refinedMean),
                },
                best_trial = bestTrial,
                trial_results = trials,
            };

            Directory.CreateDirectory(Path.GetDirectoryName(outPath)!);
            File.WriteAllText(
                outPath,
                JsonSerializer.Serialize(report, new JsonSerializerOptions { WriteIndented = true }) + Environment.NewLine
            );
            Console.WriteLine($"\nSaved report: {outPath}");

            return 0;
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"Error: {ex.Message}");
#if DEBUG
            Console.Error.WriteLine(ex);
#endif
            return 1;
        }
    }

    private static Parameters ParseParameters(string[] args)
    {
        var instanceId = "small";
        var depth = 1;
        var coarseShots = 64;
        var refinedShots = 256;
        var trials = 16;
        string? outFile = null;

        for (var i = 0; i < args.Length; i++)
        {
            switch (args[i])
            {
                case "--instance":
                    instanceId = RequireValue(args, ref i, "--instance");
                    break;
                case "--depth":
                    depth = ParsePositiveInt(RequireValue(args, ref i, "--depth"), "depth");
                    break;
                case "--coarse-shots":
                    coarseShots = ParsePositiveInt(RequireValue(args, ref i, "--coarse-shots"), "coarse-shots");
                    break;
                case "--refined-shots":
                    refinedShots = ParsePositiveInt(RequireValue(args, ref i, "--refined-shots"), "refined-shots");
                    break;
                case "--trials":
                    trials = ParsePositiveInt(RequireValue(args, ref i, "--trials"), "trials");
                    break;
                case "--out":
                    outFile = RequireValue(args, ref i, "--out");
                    break;
                default:
                    throw new ArgumentException($"Unknown argument '{args[i]}'.");
            }
        }

        if (depth < 1)
        {
            throw new ArgumentOutOfRangeException(nameof(depth), "Depth must be at least 1.");
        }

        return new Parameters(instanceId, depth, coarseShots, refinedShots, trials, outFile);
    }

    private static string RequireValue(string[] args, ref int index, string flag)
    {
        if (index + 1 >= args.Length)
        {
            throw new ArgumentException($"Expected value after '{flag}'.");
        }

        index += 1;
        return args[index];
    }

    private static int ParsePositiveInt(string value, string name)
    {
        if (!int.TryParse(value, NumberStyles.Integer, CultureInfo.InvariantCulture, out var parsed) || parsed <= 0)
        {
            throw new ArgumentException($"Argument '{name}' must be a positive integer.");
        }

        return parsed;
    }

    private static QArray<QArray<double>> ToQuantumArray(double[][] matrix)
    {
        var rows = matrix.Select(row => new QArray<double>(row)).ToArray();
        return new QArray<QArray<double>>(rows);
    }

    private static string ResolveOutputPath(Parameters parameters, string problemDir)
    {
        if (!string.IsNullOrWhiteSpace(parameters.OutFile))
        {
            return Path.GetFullPath(parameters.OutFile);
        }

        return Path.Combine(
            problemDir,
            "estimates",
            $"quantum_baseline_{parameters.InstanceId}_d{parameters.Depth}.json"
        );
    }

    private static (double Mean, double Std, double Ci95) ComputeStats(IReadOnlyList<double> values)
    {
        if (values.Count == 0)
        {
            return (0.0, 0.0, 0.0);
        }

        var mean = values.Average();
        if (values.Count == 1)
        {
            return (mean, 0.0, 0.0);
        }

        var variance = values.Sum(v => (v - mean) * (v - mean)) / (values.Count - 1);
        var std = Math.Sqrt(variance);
        var ci95 = 1.96 * std / Math.Sqrt(values.Count);
        return (mean, std, ci95);
    }

    private static string FormatAssignment(IEnumerable<long> bits)
    {
        return "[" + string.Join(",", bits.Select(bit => bit.ToString(CultureInfo.InvariantCulture))) + "]";
    }

    private static string FormatDoubleArray(IEnumerable<double> values)
    {
        return "[" + string.Join(",", values.Select(v => v.ToString("F4", CultureInfo.InvariantCulture))) + "]";
    }
}
