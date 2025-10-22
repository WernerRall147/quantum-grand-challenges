using System.Globalization;
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

internal readonly record struct Parameters(string InstanceId, int Depth, int CoarseShots, int RefinedShots);

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
            Console.WriteLine($"Shots (coarse/refined): {parameters.CoarseShots}/{parameters.RefinedShots}\n");

            using var simulator = new QuantumSimulator(randomNumberGeneratorSeed: 1337u);

            var weightArray = ToQuantumArray(weights);
            var resultTask = RunQaoaAnalysis.Run(
                simulator,
                weightArray,
                parameters.Depth,
                parameters.CoarseShots,
                parameters.RefinedShots
            );
            var result = resultTask.Result;

            var optimalValue = result.Item1;
            var optimalAssignment = result.Item2.ToArray();
            var bestBeta = result.Item3;
            var bestGamma = result.Item4;
            var coarseExpectation = result.Item5;
            var coarseSample = result.Item6;
            var coarseAssignment = result.Item7.ToArray();
            var refinedExpectation = result.Item8;
            var refinedSample = result.Item9;
            var refinedAssignment = result.Item10.ToArray();

            Console.WriteLine($"Classical optimum value : {optimalValue}");
            Console.WriteLine($"Classical assignment    : {FormatAssignment(optimalAssignment)}\n");

            Console.WriteLine("Depth-1 QAOA coarse grid search:");
            Console.WriteLine($"  Best beta  : {bestBeta}");
            Console.WriteLine($"  Best gamma : {bestGamma}");
            Console.WriteLine($"  Expectation: {coarseExpectation}");
            Console.WriteLine($"  Best sample: {coarseSample} with assignment {FormatAssignment(coarseAssignment)}\n");

            Console.WriteLine("Refined sampling:");
            Console.WriteLine($"  Expectation: {refinedExpectation}");
            Console.WriteLine($"  Best sample: {refinedSample} with assignment {FormatAssignment(refinedAssignment)}");

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
                default:
                    throw new ArgumentException($"Unknown argument '{args[i]}'.");
            }
        }

        if (depth < 1)
        {
            throw new ArgumentOutOfRangeException(nameof(depth), "Depth must be at least 1.");
        }

        return new Parameters(instanceId, depth, coarseShots, refinedShots);
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

    private static string FormatAssignment(IEnumerable<long> bits)
    {
        return "[" + string.Join(",", bits.Select(bit => bit.ToString(CultureInfo.InvariantCulture))) + "]";
    }
}
