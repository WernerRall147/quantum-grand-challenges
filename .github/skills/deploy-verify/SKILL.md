---
name: deploy-verify
description: How to confirm that a change merged to main reached production and behaves there - which workflows deploy the website and the evaluator API, how to watch them, and the checks that exercise the live site and API. Use after a merge that touches website/ or files the API image ships.
---

# Verify a deploy

Merging is not shipping. A change is live when the deploy run succeeded and production behaves
differently because of it.

## What deploys what

| Change | Workflow | Production |
|---|---|---|
| `website/**` | `.github/workflows/deploy-website.yml` | GitHub Pages: `https://wernerrall147.github.io/quantum-grand-challenges/` |
| any file the API image ships | `.github/workflows/deploy-evaluator-api.yml` | Azure Container Apps: `https://qgc-eval-api.jollysea-98a0f8cb.eastus.azurecontainerapps.io` |

The API workflow's path filter must cover every file the `Dockerfile` copies;
`agents/tests/test_container_contents.py` fails when it does not. Agents do not run deploy
workflows; merges do.

## Watch the run

```bash
gh run list --branch main --limit 10
gh run watch <run-id> --exit-status
gh run view <run-id> --json status,conclusion
```

Query the run itself, not a pull request's checks summary. The API workflow ends with its own
smoke steps (a real `/api/evaluate` call and a Q# generation request); read their output in the
log.

## Check production behaviour

- **Website:** fetch the changed page and look for the changed content, for example
  `curl -s https://wernerrall147.github.io/quantum-grand-challenges/compare/ | grep -c "<text you changed>"`.
  Pages can take a few minutes after the run finishes.
- **API reference data:** `/api/reference-problems` serves `problems/reference_index.json` reshaped
  by `knowledge/search/kb_client.py`. Compare the live response with that function's output on
  `main`, not with the raw file.
- **Code generation:** `python tooling/check_codegen_live.py` sends real prompts to the live API
  and prints one row per prompt with its result.

## From the cloud agent

The cloud agent's firewall blocks the API host, and GitHub Pages may be blocked too. Do not
report production as verified from there. Leave it to the deploy workflow's smoke steps, the
scheduled `.github/workflows/uptime-evaluator-api.yml` and
`.github/workflows/codegen-live-check.yml`, or a human running the commands above.
