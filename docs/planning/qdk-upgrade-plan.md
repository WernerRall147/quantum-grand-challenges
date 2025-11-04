# Quantum SDK Upgrade Plan

## 1. Current Baseline
- Repository authored against `Microsoft.Quantum.Sdk` **0.28.302812** targeting **.NET 6.0**.
- Q# projects confirmed to build/run only when .NET 6 runtime is available; higher runtimes emit `NETSDK1138` warning.
- Analyzer tooling (Python) orchestrates `dotnet build/run` assuming Release net6.0 output paths.

## 2. Upgrade Goals
1. Adopt the latest stable QDK (`Microsoft.Quantum.Sdk`) to unlock compiler/runtime fixes and new libraries.
2. Migrate Q# projects to the corresponding supported target framework (likely `net8.0`).
3. Preserve current QAERisk functionality, output schema, and analyzer automation.

## 3. Prerequisites
- Install the required .NET SDK version (expected **.NET 8.0 SDK**).
- Verify host IDE tooling (VS Code QDK extension) supports the desired QDK version.
- Capture baseline artifacts for comparison (`quantum_estimate.json`, plots, analyzer report).
- Ensure clean git working tree before starting the migration branch.

## 4. Work Plan
### Phase A: Environment Spike
- Create feature branch `feature/qdk-upgrade-spike`.
- Install .NET 8.0 SDK and verify with `dotnet --list-sdks`.
- Update one representative project (`problems/03_qae_risk/qsharp/QAERisk.csproj`) to the new `Microsoft.Quantum.Sdk` version and target framework.

### Phase B: Code & Config Updates
- Adjust shared Q# utilities (e.g., `libs/common/Utils.qs`) to satisfy any namespace or API changes.
- Update analyzer scripts if output directories/names change (e.g., `bin/Release/net8.0`).
- Refresh `global.json` if the repo pins .NET versions (currently none, but verify).

### Phase C: Validation Suite
- `dotnet build` and `dotnet run` for each Q# project.
- Execute `py -3.11 problems/03_qae_risk/python/analyze.py --ensemble-runs 2` to confirm orchestration.
- Compare new JSON outputs/plots against baseline to detect regressions.

### Phase D: Documentation & Cleanup
- Document upgrade impacts in `README.md` and per-problem READMEs.
- Capture notable API changes, warnings, or workarounds.
- Remove temporary logs; ensure consistent formatting.

## 5. Risk & Mitigations
- **API Breaking Changes**: Map compile errors to new APIs; consult QDK release notes.
- **Performance regressions**: Re-run ensemble analysis; adjust repetition counts if runtime changes.
- **Tooling drift**: Ensure CI and developer machines adopt compatible SDK; update contributor guidelines.
- **Dependency interactions**: Validate shared utilities for all problems, not just QAERisk.

## 6. Rollback Strategy
- If critical blockers arise, revert csproj changes and reapply `Microsoft.Quantum.Sdk` 0.28.x on the feature branch.
- Preserve baseline artifacts to demonstrate parity upon rollback.
- Clearly log encountered blockers for future upgrade attempts.

## 7. Open Questions
- Do we require Azure Quantum integration updates (extensions, resource estimators) once on new QDK?
- Are there upstream plans to change the project layout (e.g., move to QIR features) that should align with this upgrade?
- Will other problems (e.g., `01_hubbard`) migrate simultaneously or in a staggered fashion?

## 8. Next Actions
1. Commit this plan to `docs/planning/qdk-upgrade-plan.md`.
2. Stage and push current work (`git add`, `git commit -m "docs: add QDK upgrade plan"`, `git push`).
3. Branch from the latest mainline and begin Phase A when ready.

## 9. Execution Log
- 2025-10-26 19:50 UTC — Verified installed .NET SDKs via `dotnet --list-sdks`; host contains 6.0.428, 7.0.120, 8.0.121, 9.0.305, 9.0.306.
### [2025-10-26] Phase A: Environment and SDK Verification

1. Verified .NET SDKs installed: 6.0, 7.0, 8.0, 9.0 (`dotnet --list-sdks`)
2. Created feature branch: `feature/qdk-upgrade-spike`
3. Queried NuGet for Microsoft.Quantum.Sdk versions (`https://api.nuget.org/v3-flatcontainer/microsoft.quantum.sdk/index.json`)
4. Result: Latest stable version is 0.28.302812 (no newer stable QDK available)
5. No code changes made to csproj or Q# files yet.

**Interim Conclusion:**
- Upgrade blocked until newer QDK is released. All steps logged for future reference.

---

### [2025-10-26] Phase B: Recommendations and Next Steps

**Blockers:**
- No newer stable QDK available on NuGet as of this date.
- Q# projects require .NET 6.0 runtime and Microsoft.Quantum.Sdk 0.28.302812.

**Recommendations:**
1. Periodically re-check NuGet for new QDK releases (both stable and pre-release).
2. When a new QDK is available:
	- Update csproj to target the new SDK and .NET version.
	- Run full environment and build validation.
	- Document all errors, warnings, and fixes in this log.
3. Consider testing pre-release QDK versions in a separate branch if urgent.
4. Keep all environment checks and migration steps reproducible for future upgrades.

**Lessons Learned:**
- Always verify NuGet before attempting migration.
- Document every step, error code, and workaround for team knowledge transfer.
- Maintain a rollback plan in case of breaking changes.

**Next Actions:**
- Wait for new QDK release.
- Revisit this plan and restart migration when available.
- Continue to log all findings and environment changes here.
