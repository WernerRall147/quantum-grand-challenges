# Local Actions fallback

Hosted runners remain the default. When hosted minutes run out, or you want CI on the
laptop, use the shared runner tool `tools/self-hosted-runner/ci-runner.ps1` in the
private repository
[WernerRall147/aqerra](https://github.com/WernerRall147/aqerra/tree/main/tools/self-hosted-runner).
It starts isolated, single-job Docker runners on the laptop and serves this repository
through `-Repo`. Keep one copy of the tool per laptop: `up` and `down` refuse a
repository that another copy's workers are already serving. Its README covers resource
limits, logs and the security limits of containers on a developer network.

From the aqerra clone, in PowerShell 7 (`pwsh`):

```powershell
$runner = ".\tools\self-hosted-runner\ci-runner.ps1"
$repo = "WernerRall147/quantum-grand-challenges"
pwsh $runner check
pwsh $runner up -Repo $repo -AllowPublic -PipIndex <your pip index>
gh variable set CI_RUNNER -R $repo --body '["self-hosted","linux","x64","local-fallback"]'
pwsh $runner status -Repo $repo
pwsh $runner down -Repo $repo
```

Run the `gh variable set` line from PowerShell 7: Windows PowerShell 5.1 strips the
double quotes from the argument, and the variable then holds invalid JSON.

## The variables this repository reads

Each workflow job here picks its runner from one of two GitHub Actions **repository
configuration variables**, not secrets (Settings > Secrets and variables > Actions >
Variables):

- `CI_RUNNER` for CI and scheduled checks.
- `DEPLOY_RUNNER` for deployments and the nightly Azure jobs.

`["self-hosted","linux","x64","local-fallback"]` selects the laptop. An unset variable
selects `ubuntu-latest`. A quoted JSON string such as `"ubuntu-latest"` also works; bare
`ubuntu-latest` is not valid JSON and fails workflow evaluation.

The tool's `up` sets neither. It starts the workers and a heartbeat and sets
`CI_LOCAL_RUNNER` and `LOCAL_RUNNER_ALIVE_UNTIL`, and `switch` sets `CI_RUNNER_MODE`.
Those drive the automatic GitHub-hosted-then-laptop routing in aqerra's workflows, which
this repository has not adopted, so `up` alone sends no job here to the laptop and
`switch local` changes nothing. Set `CI_RUNNER` by hand as above. Leave `DEPLOY_RUNNER`
unset unless you explicitly want deploys and the nightly Azure jobs on the laptop; the
tool's `-Deploy` sets `DEPLOY_LOCAL_RUNNER`, which this repository does not read either.

`down` removes `CI_RUNNER` and `DEPLOY_RUNNER` along with the tool's own variables, and
`switch hosted` removes them too. `down` refuses while a job is running unless you pass
`-Force`. Neither command dispatches workflows.

## No automatic fallback here

While `CI_RUNNER` is set, CI jobs wait for the laptop even when GitHub-hosted runners are
free, and that includes scheduled runs such as the evaluator uptime probe and Nightly.
If the laptop sleeps, reboots or loses its network, those jobs stay queued, and GitHub
cancels a self-hosted job that has been queued for 24 hours
([Actions limits](https://docs.github.com/en/actions/reference/limits)). Workers do not
survive a reboot or sign-out, but `CI_RUNNER` does. So:

- Keep the laptop awake and plugged in while `CI_RUNNER` is set.
- Run `down` before you leave the laptop. If `down` cannot reach GitHub it stops the
  local side only; run it again, because jobs keep queueing for the laptop until
  `CI_RUNNER` is gone.
- Queued jobs keep the labels they were given: after switching, cancel them and start
  them again.

## Python packages

Jobs here install Python packages with pip. On a network that blocks
`files.pythonhosted.org` (`check` reports it as `WARN`), every `pip install` on the
laptop fails. Pass a mirror to `up` with `-PipIndex <url>`; `pip config list` shows the
one your own pip uses. The tool never reads pip's configuration itself. If the URL
carries a token, set `PIP_INDEX_URL` in the shell that runs `up` instead, so the token is
not left on the command line.

## Public repository

`up` refuses a public repository without `-AllowPublic`. Fork pull requests stay on
GitHub-hosted runners, including fork PRs from collaborators: every `runs-on` that reads
`CI_RUNNER` or `DEPLOY_RUNNER` first sends a pull request from a fork to `ubuntu-latest`.
Only trusted same-repository branches should execute locally. Do not remove that guard,
or enable local execution for `pull_request_target` workflows that check out untrusted
code.

Copilot setup remains hosted to preserve the cloud agent environment. Devcontainer
validation also remains hosted because it needs Docker inside the job; local workers have
no Docker socket or privileged mode. The Pages artifact action is composite/JavaScript and
can run unchanged on these Linux workers.
