The smartest design is **not** “put the whole repo into a vector DB.”
For your scenario, I’d build a **Code Knowledge Graph + Azure AI Search + Copilot MCP tool layer**.

Copilot already has repository indexing and semantic code search, but GitHub’s own docs frame that as context enrichment, not as a deterministic dependency engine. Copilot repository indexing helps it answer questions about code structure and logic, and Copilot cloud agent uses semantic code search when it does not know the exact terms to search for. ([GitHub Docs][1]) For safe cleanup of unused code, you need exact references from the compiler/analyzer layer, not only semantic search.

## Recommended architecture

```text
GitHub repo
  └── CI indexer on every merge / nightly
        ├── Roslyn / MSBuild analysis
        │     ├── projects
        │     ├── symbols
        │     ├── references
        │     ├── call graph
        │     ├── inheritance / interface implementation
        │     ├── package refs
        │     └── unused candidates
        │
        ├── Azure AI Search
        │     ├── code chunks
        │     ├── docs / website knowledge
        │     ├── READMEs / ADRs / runbooks
        │     └── semantic + keyword retrieval
        │
        ├── Cosmos DB or graph store
        │     ├── exact dependency graph
        │     ├── symbol-to-symbol edges
        │     ├── file-to-symbol edges
        │     └── repo commit snapshot
        │
        └── MCP server for Copilot
              ├── find_symbol
              ├── find_references
              ├── get_dependency_path
              ├── get_unused_candidates
              ├── get_impacted_projects
              ├── get_relevant_docs
              └── explain_safe_delete_plan
```

## The short answer

Use **Azure AI Search for discovery** and **Cosmos DB / graph storage for exact dependency links**.

For your 20 `.sln` files, I would not make Copilot scan all files every time. I would precompute a **symbol graph** from Roslyn/MSBuild, store it by commit SHA, and expose it to Copilot through **MCP tools**. GitHub supports repository-level MCP configuration so Copilot cloud agent and Copilot code review can use external tools and data sources. ([GitHub Docs][2])

## Why vector search alone is not enough

Azure AI Search is excellent for “find where this business rule is implemented” because it supports hybrid search: keyword + vector search in a single query, merged with Reciprocal Rank Fusion. ([Microsoft Learn][3]) Microsoft also recommends hybrid queries with semantic ranking for relevance improvements in many cases. ([Microsoft Learn][4])

But “is this unused?” is not a semantic question. It is a **compiler/reference question**.

For example, this is dangerous to decide with embeddings:

```csharp
public class PaymentValidator
```

It may look unused in text search, but it could be used by:

```csharp
services.AddScoped<IPaymentValidator, PaymentValidator>();
```

or reflection:

```csharp
Type.GetType("MyApp.PaymentValidator")
```

or configuration, Razor, XAML, JSON serialization, routing, tests, dependency injection, plugins, or public API consumers.

So the deletion workflow should be:

```text
AI Search finds likely area
→ Roslyn graph confirms exact references
→ MCP returns compact evidence to Copilot
→ Copilot edits only scoped files
→ build/tests prove safety
```

## Storage choice

| Need                              | Best storage                                |
| --------------------------------- | ------------------------------------------- |
| Search code/docs by meaning       | **Azure AI Search**                         |
| Exact symbol references           | **Cosmos DB / graph-style adjacency lists** |
| Fast “who uses this?” lookup      | **Cosmos DB with precomputed edges**        |
| Semantic docs + website knowledge | **Azure AI Search**                         |
| Copilot access                    | **MCP server**                              |
| Human browsing                    | Website over the same index/graph           |
| Safe unused cleanup               | Roslyn graph + build/test verification      |

Cosmos DB now supports vector search as well, so it can technically act as a vector store. ([Microsoft Learn][5]) But for your use case, I would not make Cosmos your primary code search engine. Use Cosmos for **structured dependency facts** and Azure AI Search for **retrieval over code/docs**.

## What to store in the dependency graph

For each repo commit:

```json
{
  "repo": "your-org/your-repo",
  "commit": "abc123",
  "solution": "App.sln",
  "project": "src/Billing/Billing.csproj",
  "targetFramework": "net8.0",
  "symbolId": "Billing.Services.PaymentValidator.Validate(PaymentRequest)",
  "symbolKind": "Method",
  "file": "src/Billing/Services/PaymentValidator.cs",
  "startLine": 42,
  "endLine": 87,
  "githubUrl": ".../blob/abc123/src/Billing/Services/PaymentValidator.cs#L42-L87",
  "references": [
    {
      "fromSymbolId": "CheckoutController.Submit(OrderRequest)",
      "fromFile": "src/Web/Controllers/CheckoutController.cs",
      "line": 118,
      "edgeType": "calls"
    }
  ],
  "riskFlags": [
    "public",
    "registered-in-di",
    "covered-by-tests"
  ]
}
```

At minimum, store these edge types:

```text
Project → ProjectReference
Project → PackageReference
File → DeclaresSymbol
Symbol → ReferencesSymbol
Symbol → CallsSymbol
Class → ImplementsInterface
Class → InheritsClass
Method → OverridesMethod
Controller/Endpoint → Route
Service → DIRegistration
Test → CoversOrReferencesSymbol
Config → BindsToType
```

For .NET, use **Roslyn** as the source of truth. Microsoft’s `SymbolFinder.FindReferencesAsync` is specifically designed to find references to a symbol throughout a solution. ([Microsoft Learn][6]) `SymbolFinder` also exposes methods for implementations, overrides, derived types, and source declarations, which are exactly the building blocks you need for safe dependency analysis. ([Microsoft Learn][7])

## Best design for Copilot specifically

Give Copilot three layers of context:

### 1. Native repo context

Let Copilot use its own repository index. GitHub says repository indexing improves context-enriched answers and is used by Copilot Chat and Copilot cloud agent. ([GitHub Docs][1])

### 2. Repository instructions

Add:

```text
.github/copilot-instructions.md
.github/instructions/code-cleanup.instructions.md
```

Tell Copilot:

```md
Before removing code, always call the code graph tools:
1. find_symbol
2. find_references
3. get_impacted_projects
4. get_delete_risk
5. get_build_test_plan

Do not remove public APIs, reflection-used types, DI-registered classes, route handlers, config-bound models, generated code, or symbols with external package exposure unless explicitly requested.
```

GitHub supports repository-wide custom instructions via `.github/copilot-instructions.md`, and path-specific instructions via `.github/instructions/**/*.instructions.md` in supported environments. ([GitHub Docs][8])

### 3. MCP tools

Expose your graph and Azure AI Search through MCP.

Example tools:

```text
find_symbol(name)
find_references(symbolId)
get_callers(symbolId)
get_implementations(interfaceId)
get_delete_risk(symbolId)
get_impacted_projects(symbolId)
search_code_and_docs(query)
get_related_docs(symbolId)
create_cleanup_plan(symbolId)
```

This is better than stuffing context into prompts because Copilot can ask for the exact slice it needs.

## Best flow for “clean up unused items”

```text
1. Index all 20 solutions.
2. Normalize duplicate projects across solutions.
3. Generate symbol graph per project + target framework.
4. Mark unused candidates.
5. Exclude dangerous candidates:
   - public API
   - DI registrations
   - reflection
   - routing
   - Razor/XAML
   - generated code
   - serialization models
   - migration code
   - plugin/discovery patterns
6. Ask Copilot to remove one candidate cluster at a time.
7. Run build + tests.
8. Re-index after the PR.
```

For 20 `.sln` files, the important part is deduping by:

```text
repo + commit + project path + target framework + configuration
```

Do not treat each `.sln` as an isolated universe. A project may appear in multiple solutions.

## My recommendation for your Azure setup

Since you already have Azure AI Search running, I would do this:

```text
Azure AI Search
  Index 1: code_chunks
  Index 2: docs_knowledge
  Index 3: tool_docs / website content

Cosmos DB
  Container 1: symbols
  Container 2: edges
  Container 3: project_snapshots
  Container 4: cleanup_candidates

MCP API
  /tools/findSymbol
  /tools/findReferences
  /tools/getDependencyPath
  /tools/getUnusedCandidates
  /tools/searchKnowledge
```

Partition Cosmos roughly like:

```text
/repoCommitProject
```

or:

```text
/repo + /commit
```

depending on query volume. For “who references this symbol?”, create a reverse edge document so lookup is direct and fast:

```json
{
  "id": "reverse:Billing.PaymentValidator.Validate",
  "symbolId": "Billing.PaymentValidator.Validate",
  "inboundReferences": [
    "CheckoutController.Submit",
    "PaymentTests.ValidPayment_ReturnsTrue"
  ]
}
```

That avoids expensive graph traversal during Copilot conversations.

## Final answer

The best solution is:

**Roslyn-generated Code Knowledge Graph + Azure AI Search hybrid retrieval + Cosmos DB adjacency storage + MCP tools for Copilot.**

Use Copilot’s native repository indexing as the baseline, but do not rely on it for safe unused-code cleanup. Let Copilot reason and edit, but make your own graph provide the exact dependency truth.

[1]: https://docs.github.com/en/copilot/concepts/context/repository-indexing "Indexing repositories for GitHub Copilot - GitHub Docs"
[2]: https://docs.github.com/copilot/how-tos/agents/copilot-coding-agent/extending-copilot-coding-agent-with-mcp "Configure MCP servers for your repository - GitHub Docs"
[3]: https://learn.microsoft.com/en-us/azure/search/hybrid-search-overview "Hybrid Search Overview - Azure AI Search | Microsoft Learn"
[4]: https://learn.microsoft.com/en-us/azure/search/hybrid-search-how-to-query "Create a Hybrid Query - Azure AI Search | Microsoft Learn"
[5]: https://learn.microsoft.com/en-us/azure/cosmos-db/gen-ai/vector-search-overview "Vector Similarity Search - Azure Cosmos DB | Microsoft Learn"
[6]: https://learn.microsoft.com/en-us/dotnet/api/microsoft.codeanalysis.findsymbols.symbolfinder.findreferencesasync?view=roslyn-dotnet-5.0.0 "SymbolFinder.FindReferencesAsync Method (Microsoft.CodeAnalysis.FindSymbols) | Microsoft Learn"
[7]: https://learn.microsoft.com/en-us/dotnet/api/microsoft.codeanalysis.findsymbols.symbolfinder?view=roslyn-dotnet-5.0.0 "SymbolFinder Class (Microsoft.CodeAnalysis.FindSymbols) | Microsoft Learn"
[8]: https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot "Adding repository custom instructions for GitHub Copilot - GitHub Docs"
