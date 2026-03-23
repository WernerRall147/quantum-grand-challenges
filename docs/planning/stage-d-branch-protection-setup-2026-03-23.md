# Stage D Branch Protection Setup

Generated: 2026-03-23

## Status

Branch protection automation is prepared but could not be executed from this session because GitHub CLI authentication is not configured.

## Prerequisites

- GitHub CLI installed (`gh --version`)
- Authenticated session (`gh auth login`)
- Admin rights on `WernerRall147/quantum-grand-challenges`

## Apply Protection

From repository root, run:

```powershell
./tooling/windows/set_main_branch_protection_stage_d.ps1
```

For a solo-maintainer flow (recommended current setting), keep required approvals at zero while still enforcing required status checks:

```powershell
./tooling/windows/set_main_branch_protection_stage_d.ps1 -RequiredApprovals 0
```

For team review enforcement, increase required approvals:

```powershell
./tooling/windows/set_main_branch_protection_stage_d.ps1 -RequiredApprovals 1
```

## What It Configures

- Required status check: `Stage D Readiness Gate / stage-d-readiness`
- Strict status checks before merge
- Enforce admins
- Require configurable approving reviews
- Require conversation resolution
- Disable force push and branch deletion
