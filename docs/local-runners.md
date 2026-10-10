# Local Actions fallback

Hosted runners remain the default. When hosted minutes run out, use the shared
[runner tooling in MyRoleCSA](https://github.com/WernerRall147/MyRoleCSA/tree/main/tools/self-hosted-runner).
It starts isolated, single-job Docker runners on the laptop for this repository.

From the MyRoleCSA checkout:

```powershell
$runner = ".\tools\self-hosted-runner\ci-runner.ps1"
$repo = "WernerRall147/quantum-grand-challenges"
pwsh $runner up -Repo $repo -AllowPublic
pwsh $runner switch local -Repo $repo -AllowPublic
pwsh $runner status -Repo $repo
pwsh $runner switch hosted -Repo $repo
pwsh $runner down -Repo $repo
```

`CI_RUNNER` selects local runners for CI and scheduled checks. Deployments and
nightly Azure jobs use the separate `DEPLOY_RUNNER`; pass `-Deploy` to
`switch local` only when you explicitly want those jobs on the laptop too.
The variables hold `["self-hosted","linux","x64","local-fallback"]`. Unset
variables select `ubuntu-latest`. Switching does not dispatch workflows.

This repository is public. All fork pull requests remain on hosted runners,
including fork PRs from collaborators. Only trusted same-repository branches
should execute locally. Do not remove the fork guard or enable local execution
for `pull_request_target` workflows that check out untrusted code.

Copilot setup remains hosted to preserve the cloud agent environment. Devcontainer
validation also remains hosted because it needs Docker inside the job; local
workers have no Docker socket or privileged mode. The Pages artifact action is
composite/JavaScript and can run unchanged on these Linux workers.

Keep the laptop awake. Workers need restarting after reboot/sign-out. Queued
jobs keep their selected labels; cancel and re-run them after switching pools.
See the shared tooling README for resource limits, logs, network checks and
the security limitations of containers on a trusted developer network.
